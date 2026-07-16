import { HTMLAttributes, ReactNode } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Timeline.module.css';

export interface TimelineItem {
  id: string;
  title: ReactNode;
  description?: ReactNode;
  time?: ReactNode;
  icon?: ReactNode;
  isActive?: boolean;
}

export interface TimelineProps extends HTMLAttributes<HTMLDivElement> {
  items: TimelineItem[];
}

export function Timeline({ className, items, ...props }: TimelineProps) {
  return (
    <div className={cx(styles.timeline, className)} {...props}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <div key={item.id} className={styles.item}>
            <div className={styles.tailWrapper}>
              <div
                className={cx(
                  styles.dot,
                  item.isActive && styles.dotActive,
                  item.icon && styles.dotWithIcon
                )}
              >
                {item.icon}
              </div>
              {!isLast && <div className={styles.tail} />}
            </div>
            <div className={styles.content}>
              <div className={styles.header}>
                <h4 className={cx(styles.title, item.isActive && styles.titleActive)}>
                  {item.title}
                </h4>
                {item.time && <span className={styles.time}>{item.time}</span>}
              </div>
              {item.description && (
                <div className={styles.description}>{item.description}</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
