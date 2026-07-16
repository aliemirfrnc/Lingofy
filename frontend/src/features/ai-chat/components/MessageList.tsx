'use client';

import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { StreamingMessage } from './StreamingMessage';
import { EmptyConversation } from './EmptyConversation';
import { ConversationState } from '../models/aiModels';
import styles from './AiChat.module.css';

interface MessageListProps {
  state: ConversationState;
}

export function MessageList({ state }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Auto scroll to bottom when messages or streaming content changes
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages, state.streamingContent]);

  if (state.messages.length === 0 && !state.isStreaming) {
    return <EmptyConversation />;
  }

  return (
    <div className={styles.messageList} role="log" aria-live="polite">
      {state.messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      
      {state.isStreaming && state.streamingContent && (
        <StreamingMessage content={state.streamingContent} />
      )}
      
      {state.error && (
        <div className={styles.errorState} role="alert">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div>
            <strong>Error</strong>
            <p style={{ margin: 0 }}>{state.error.message}</p>
          </div>
        </div>
      )}
      
      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}
