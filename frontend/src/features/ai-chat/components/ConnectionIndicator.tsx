'use client';

import styles from './AiChat.module.css';

interface ConnectionIndicatorProps {
  status: string | null;
  progress: number;
}

export function ConnectionIndicator({ status, progress }: ConnectionIndicatorProps) {
  if (!status) return null;

  if (status === 'processing') {
    return (
      <div className={`${styles.indicator} ${styles.indicatorProcessing}`} role="status">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'spin 2s linear infinite' }}>
          <line x1="12" y1="2" x2="12" y2="6"></line>
          <line x1="12" y1="18" x2="12" y2="22"></line>
          <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
          <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
          <line x1="2" y1="12" x2="6" y2="12"></line>
          <line x1="18" y1="12" x2="22" y2="12"></line>
          <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
          <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
        </svg>
        Background Process: {progress}%
      </div>
    );
  }

  if (status === 'completed') {
    return (
      <div className={`${styles.indicator} ${styles.indicatorCompleted}`} role="status">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        Task Completed
      </div>
    );
  }

  return null;
}
