import { useState, useCallback, useEffect, useRef } from 'react';
import { Message, AIError, ConversationState } from '../models/aiModels';
import { mapToMessage } from '../mappers/aiMappers';
import { handleStreamResponse } from '../services/aiApplicationService';
import { useRealtime } from '@/features/realtime';

export function useChat() {
  const [state, setState] = useState<ConversationState>({
    id: crypto.randomUUID(),
    messages: [],
    isStreaming: false,
    streamingContent: '',
    error: null,
    jobStatus: null,
    jobProgress: 0,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => () => {
    abortControllerRef.current?.abort();
  }, []);

  useRealtime(useCallback((type: string, payload: unknown) => {
    if (type === 'job.progress') {
      const data = payload as { job_id: string; progress: number };
      setState(prev => ({ ...prev, jobProgress: data.progress, jobStatus: 'processing' }));
    } else if (type === 'job.completed') {
      setState(prev => ({ ...prev, jobProgress: 100, jobStatus: 'completed' }));
    } else if (type === 'job.failed') {
      setState(prev => ({ 
        ...prev, 
        jobStatus: 'failed', 
        error: new AIError('Arka plan işlemi başarısız oldu.', 'Unknown') 
      }));
    }
  }, []));

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || state.isStreaming) return;

    const userMessage = mapToMessage('user', content);
    
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isStreaming: true,
      streamingContent: '',
      error: null,
      jobStatus: null,
      jobProgress: 0,
    }));

    abortControllerRef.current = new AbortController();

    try {
      const generator = handleStreamResponse(content, abortControllerRef.current.signal);
      
      let fullContent = '';
      for await (const chunk of generator) {
        fullContent += chunk;
        setState(prev => ({
          ...prev,
          streamingContent: fullContent,
        }));
      }

      const assistantMessage = mapToMessage('assistant', fullContent);
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isStreaming: false,
        streamingContent: '',
      }));

    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        setState(prev => ({ ...prev, isStreaming: false }));
        return;
      }
      
      setState(prev => ({
        ...prev,
        isStreaming: false,
        error: error instanceof AIError ? error : new AIError('Bilinmeyen bir hata oluştu', 'Unknown'),
      }));
    } finally {
      abortControllerRef.current = null;
    }
  }, [state.isStreaming]);

  const cancelStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    state,
    sendMessage,
    cancelStreaming,
    clearError,
  };
}
