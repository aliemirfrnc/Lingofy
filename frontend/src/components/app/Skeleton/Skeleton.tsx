import { HTMLAttributes } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Skeleton.module.css';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animation = 'pulse',
  style,
  ...props
}: SkeletonProps) {
  return (
    <div
      className={cx(
        styles.skeleton,
        styles[`variant-${variant}`],
        styles[`animation-${animation}`],
        className
      )}
      style={{
        width: width ?? (variant === 'text' ? '100%' : undefined),
        height: height ?? (variant === 'text' ? '1em' : undefined),
        ...style,
      }}
      aria-hidden="true"
      {...props}
    />
  );
}
