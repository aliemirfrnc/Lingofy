'use client';

import { Message } from '../models/aiModels';
import styles from './AiChat.module.css';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`${styles.messageRow} ${isUser ? styles.messageRowUser : styles.messageRowAssistant}`}>
      <div 
        className={`${styles.messageBubble} ${isUser ? styles.bubbleUser : styles.bubbleAssistant}`}
        role="log"
      >
        {message.content}
      </div>
    </div>
  );
}
