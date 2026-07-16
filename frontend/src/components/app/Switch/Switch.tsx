import { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Switch.module.css';

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
}

export const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, label, error, id: externalId, disabled, ...props }, ref) => {
    const internalId = useId();
    const id = externalId || internalId;
    const errorId = `${id}-error`;

    return (
      <div className={cx(styles.container, className)}>
        <div className={styles.wrapper}>
          <div className={styles.switchWrapper}>
            <input
              type="checkbox"
              role="switch"
              id={id}
              ref={ref}
              disabled={disabled}
              aria-invalid={!!error}
              aria-describedby={error ? errorId : undefined}
              className={styles.input}
              {...props}
            />
            <span className={styles.slider} aria-hidden="true" />
          </div>
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

Switch.displayName = 'Switch';
