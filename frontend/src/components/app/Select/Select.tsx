import { SelectHTMLAttributes, forwardRef, useId } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Select.module.css';

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      fullWidth = true,
      id: externalId,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const internalId = useId();
    const id = externalId || internalId;
    const errorId = `${id}-error`;
    const helperId = `${id}-helper`;

    const ariaDescribedBy = error ? errorId : helperText ? helperId : undefined;

    return (
      <div className={cx(styles.container, fullWidth && styles.fullWidth, className)}>
        {label && (
          <label htmlFor={id} className={styles.label}>
            {label}
          </label>
        )}
        <div className={styles.selectWrapper}>
          <select
            id={id}
            ref={ref}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={ariaDescribedBy}
            className={cx(styles.select, error && styles.hasError)}
            {...props}
          >
            {children}
          </select>
          <div className={styles.iconWrapper} aria-hidden="true">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </div>
        {error && (
          <span id={errorId} className={styles.errorText} role="alert">
            {error}
          </span>
        )}
        {!error && helperText && (
          <span id={helperId} className={styles.helperText}>
            {helperText}
          </span>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
