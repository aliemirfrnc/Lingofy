'use client';

import { ReactNode, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cx } from '@/lib/app/utils';
import styles from './Toast.module.css';

export interface ToastProps {
  id: string;
  title?: ReactNode;
  message: ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'error';
  duration?: number;
  onClose: (id: string) => void;
  className?: string;
}

export function Toast({
  id,
  title,
  message,
  variant = 'info',
  duration = 5000,
  onClose,
  className,
}: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, id, onClose]);

  return (
    <div
      className={cx(styles.toast, styles[`variant-${variant}`], className)}
      role="alert"
      aria-live="assertive"
    >
      <div className={styles.iconWrapper} aria-hidden="true">
        {variant === 'success' && (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        )}
        {variant === 'error' && (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        )}
        {variant === 'warning' && (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        )}
        {variant === 'info' && (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
        )}
      </div>
      <div className={styles.content}>
        {title && <h5 className={styles.title}>{title}</h5>}
        <div className={styles.message}>{message}</div>
      </div>
      <button
        className={styles.closeButton}
        onClick={() => onClose(id)}
        aria-label="Close notification"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  );
}

export interface ToastContainerProps {
  toasts: ToastProps[];
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export function ToastContainer({ toasts, position = 'bottom-right' }: ToastContainerProps) {
  if (typeof window === 'undefined') return null;
  if (toasts.length === 0) return null;

  return createPortal(
    <div className={cx(styles.container, styles[`position-${position}`])}>
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} />
      ))}
    </div>,
    document.body
  );
}
