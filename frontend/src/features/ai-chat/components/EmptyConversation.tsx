'use client';

import styles from './AiChat.module.css';

export function EmptyConversation() {
  return (
    <div className={styles.emptyState}>
      <div className={styles.emptyIcon}>👋</div>
      <h3 style={{ margin: '0 0 var(--spacing-sm) 0', color: 'var(--color-text-primary)' }}>
        Welcome to AI Mentor
      </h3>
      <p style={{ maxWidth: '400px', margin: 0 }}>
        Ask me anything about language learning, translations, grammar, or general questions. I&apos;m here to help you practice!
      </p>
    </div>
  );
}
