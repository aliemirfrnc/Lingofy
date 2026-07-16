import { HTMLAttributes, ReactNode } from 'react';
import { cx } from '@/lib/app/utils';
import { Button } from '@/components/app/Button';
import styles from './EmptyState.module.css';

export interface EmptyStateProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  icon?: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  fullPage?: boolean;
}

export function EmptyState({
  className,
  title = 'No results found',
  description = 'Try adjusting your search or filters.',
  icon,
  actionLabel,
  onAction,
  fullPage = false,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cx(styles.container, fullPage && styles.fullPage, className)}
      {...props}
    >
      <div className={styles.iconWrapper} aria-hidden="true">
        {icon || (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={styles.icon}
          >
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        )}
      </div>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.description}>{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction} className={styles.actionButton}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
