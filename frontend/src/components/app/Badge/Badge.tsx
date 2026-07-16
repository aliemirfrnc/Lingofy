import { HTMLAttributes } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Badge.module.css';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export function Badge({
  className,
  variant = 'primary',
  size = 'md',
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cx(
        styles.badge,
        styles[`variant-${variant}`],
        styles[`size-${size}`],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
