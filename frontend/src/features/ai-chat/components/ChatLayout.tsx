'use client';

import { useChat } from '../hooks/useChat';
import { MessageList } from './MessageList';
import { PromptInput } from './PromptInput';
import { ConnectionIndicator } from './ConnectionIndicator';
import styles from './AiChat.module.css';

export function ChatLayout() {
  const { state, sendMessage, cancelStreaming } = useChat();

  return (
    <div className={styles.layout}>
      <div className={styles.chatArea}>
        <ConnectionIndicator status={state.jobStatus} progress={state.jobProgress} />
        <MessageList state={state} />
      </div>
      <div className={styles.inputArea}>
        <PromptInput 
          onSend={sendMessage}
          onCancel={cancelStreaming}
          isStreaming={state.isStreaming}
        />
      </div>
    </div>
  );
}
