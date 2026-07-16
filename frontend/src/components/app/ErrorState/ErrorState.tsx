import { HTMLAttributes } from 'react';
import { cx } from '@/lib/app/utils';
import { Button } from '@/components/app/Button';
import styles from './ErrorState.module.css';

export interface ErrorStateProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  message?: string;
  onRetry?: () => void;
  fullPage?: boolean;
}

export function ErrorState({
  className,
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  onRetry,
  fullPage = false,
  ...props
}: ErrorStateProps) {
  return (
    <div
      className={cx(styles.container, fullPage && styles.fullPage, className)}
      role="alert"
      aria-live="assertive"
      {...props}
    >
      <div className={styles.iconWrapper} aria-hidden="true">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={styles.icon}
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.message}>{message}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry} className={styles.retryButton}>
          Try Again
        </Button>
      )}
    </div>
  );
}
