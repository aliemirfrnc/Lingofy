import { HTMLAttributes } from 'react';
import Image from 'next/image';
import { cx } from '@/lib/app/utils';
import styles from './Avatar.module.css';

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Avatar({
  className,
  src,
  alt = '',
  fallback,
  size = 'md',
  ...props
}: AvatarProps) {
  return (
    <div
      className={cx(styles.avatar, styles[`size-${size}`], className)}
      {...props}
    >
      {src ? (
        <Image
          src={src}
          alt={alt}
          fill
          className={styles.image}
          sizes="(max-width: 768px) 100vw, 50vw"
        />
      ) : (
        <span className={styles.fallback}>
          {fallback || alt.charAt(0).toUpperCase() || '?'}
        </span>
      )}
    </div>
  );
}
