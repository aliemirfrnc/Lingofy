import { HTMLAttributes, forwardRef } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Card.module.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'outlined' | 'flat';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  as?: React.ElementType;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = 'elevated',
      padding = 'md',
      as: Component = 'div',
      children,
      ...props
    },
    ref
  ) => {
    return (
      <Component
        ref={ref}
        className={cx(
          styles.card,
          styles[`variant-${variant}`],
          styles[`padding-${padding}`],
          className
        )}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

Card.displayName = 'Card';
