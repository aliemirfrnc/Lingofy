import { InputHTMLAttributes, forwardRef, ReactNode, useId } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Input.module.css';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      fullWidth = true,
      id: externalId,
      disabled,
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
        <div className={styles.inputWrapper}>
          {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
          <input
            id={id}
            ref={ref}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={ariaDescribedBy}
            className={cx(
              styles.input,
              error && styles.hasError,
              leftIcon && styles.hasLeftIcon,
              rightIcon && styles.hasRightIcon
            )}
            {...props}
          />
          {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
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

Input.displayName = 'Input';
