import { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Checkbox.module.css';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, id: externalId, disabled, ...props }, ref) => {
    const internalId = useId();
    const id = externalId || internalId;
    const errorId = `${id}-error`;

    return (
      <div className={cx(styles.container, className)}>
        <div className={styles.wrapper}>
          <input
            type="checkbox"
            id={id}
            ref={ref}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : undefined}
            className={cx(styles.input, error && styles.hasError)}
            {...props}
          />
          {label && (
            <label
              htmlFor={id}
              className={cx(styles.label, disabled && styles.disabled)}
            >
              {label}
            </label>
          )}
        </div>
        {error && (
          <span id={errorId} className={styles.errorText} role="alert">
            {error}
          </span>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';
