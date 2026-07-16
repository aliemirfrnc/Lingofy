import { HTMLAttributes } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './LoadingState.module.css';

export interface LoadingStateProps extends HTMLAttributes<HTMLDivElement> {
  message?: string;
  fullPage?: boolean;
}

export function LoadingState({
  className,
  message = 'Loading...',
  fullPage = false,
  ...props
}: LoadingStateProps) {
  return (
    <div
      className={cx(styles.container, fullPage && styles.fullPage, className)}
      role="status"
      aria-live="polite"
      {...props}
    >
      <div className={styles.spinnerWrapper}>
        <svg
          className={styles.spinner}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
            strokeDasharray="32"
            strokeLinecap="round"
            opacity="0.25"
          />
          <path
            d="M12 2a10 10 0 0 1 10 10"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
          />
        </svg>
      </div>
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
}
