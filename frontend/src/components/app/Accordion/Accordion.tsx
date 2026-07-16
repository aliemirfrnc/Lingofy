'use client';

import { HTMLAttributes, ReactNode, useState } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Accordion.module.css';

export interface AccordionItem {
  id: string;
  title: ReactNode;
  content: ReactNode;
}

export interface AccordionProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onChange'> {
  items: AccordionItem[];
  defaultExpandedIds?: string[];
  allowMultiple?: boolean;
}

export function Accordion({
  className,
  items,
  defaultExpandedIds = [],
  allowMultiple = false,
  ...props
}: AccordionProps) {
  const [expandedIds, setExpandedIds] = useState<string[]>(defaultExpandedIds);

  const toggleItem = (id: string) => {
    if (expandedIds.includes(id)) {
      setExpandedIds(expandedIds.filter((item) => item !== id));
    } else {
      if (allowMultiple) {
        setExpandedIds([...expandedIds, id]);
      } else {
        setExpandedIds([id]);
      }
    }
  };

  return (
    <div className={cx(styles.accordion, className)} {...props}>
      {items.map((item) => {
        const isExpanded = expandedIds.includes(item.id);
        const buttonId = `accordion-button-${item.id}`;
        const panelId = `accordion-panel-${item.id}`;

        return (
          <div key={item.id} className={styles.item}>
            <button
              id={buttonId}
              aria-expanded={isExpanded}
              aria-controls={panelId}
              className={styles.button}
              onClick={() => toggleItem(item.id)}
            >
              <span className={styles.title}>{item.title}</span>
              <svg
                className={cx(styles.icon, isExpanded && styles.iconExpanded)}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            <div
              id={panelId}
              role="region"
              aria-labelledby={buttonId}
              className={cx(styles.panel, isExpanded && styles.panelExpanded)}
            >
              <div className={styles.content}>{item.content}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
