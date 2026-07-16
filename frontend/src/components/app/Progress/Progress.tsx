import { HTMLAttributes } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Progress.module.css';

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  variant?: 'primary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
}

export function Progress({
  className,
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  ...props
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      className={cx(styles.container, styles[`size-${size}`], className)}
      {...props}
    >
      <div
        className={cx(styles.bar, styles[`variant-${variant}`])}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
