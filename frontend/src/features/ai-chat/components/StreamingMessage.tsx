'use client';

import styles from './AiChat.module.css';

interface StreamingMessageProps {
  content: string;
}

export function StreamingMessage({ content }: StreamingMessageProps) {
  return (
    <div className={`${styles.messageRow} ${styles.messageRowAssistant}`}>
      <div 
        className={`${styles.messageBubble} ${styles.bubbleAssistant}`}
        role="log"
        aria-live="polite"
      >
        {content}
        <span style={{ display: 'inline-block', width: '8px', height: '16px', backgroundColor: 'var(--color-primary)', animation: 'blink 1s step-end infinite', marginLeft: '4px', verticalAlign: 'middle' }} />
      </div>
    </div>
  );
}
