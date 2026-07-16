'use client';

import React, { useRef, useEffect } from 'react';
import styles from './AiChat.module.css';

interface PromptInputProps {
  onSend: (message: string) => void;
  onCancel: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export function PromptInput({ onSend, onCancel, isStreaming, disabled }: PromptInputProps) {
  const [input, setInput] = React.useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isStreaming && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={styles.form}>
      <textarea
        ref={textareaRef}
        className={styles.textarea}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message (Shift+Enter for new line)..."
        disabled={disabled || isStreaming}
        aria-label="Chat input"
        rows={1}
      />
      {isStreaming ? (
        <button 
          className={`${styles.sendButton} ${styles.cancelButton}`} 
          onClick={onCancel}
          aria-label="Cancel generating"
          title="Stop Generating"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 6h12v12H6z" />
          </svg>
        </button>
      ) : (
        <button 
          className={styles.sendButton} 
          onClick={handleSubmit}
          disabled={!input.trim() || disabled}
          aria-label="Send message"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      )}
    </div>
  );
}
