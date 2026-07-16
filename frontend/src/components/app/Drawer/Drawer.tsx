'use client';

import { ReactNode, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cx } from '@/lib/app/utils';
import styles from './Drawer.module.css';

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  position?: 'left' | 'right';
  title?: ReactNode;
  className?: string;
}

export function Drawer({
  isOpen,
  onClose,
  children,
  position = 'right',
  title,
  className,
}: DrawerProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      document.addEventListener('keydown', handleEscape);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div className={styles.overlay} onClick={onClose} role="presentation">
      <div
        className={cx(styles.drawer, styles[`position-${position}`], className)}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={typeof title === 'string' ? title : 'Drawer'}
      >
        <div className={styles.header}>
          {title && <div className={styles.title}>{title}</div>}
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close drawer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div className={styles.content}>{children}</div>
      </div>
    </div>,
    document.body
  );
}
