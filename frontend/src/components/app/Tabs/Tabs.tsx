'use client';

import { HTMLAttributes, ReactNode, useState, KeyboardEvent, useRef } from 'react';
import { cx } from '@/lib/app/utils';
import styles from './Tabs.module.css';

export interface TabItem {
  id: string;
  label: ReactNode;
  content: ReactNode;
  disabled?: boolean;
}

export interface TabsProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onChange'> {
  items: TabItem[];
  defaultSelectedId?: string;
  onChange?: (id: string) => void;
}

export function Tabs({
  className,
  items,
  defaultSelectedId,
  onChange,
  ...props
}: TabsProps) {
  const [selectedId, setSelectedId] = useState(defaultSelectedId || items[0]?.id);
  const tabListRef = useRef<HTMLDivElement>(null);

  const handleTabChange = (id: string) => {
    setSelectedId(id);
    onChange?.(id);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLButtonElement>, index: number) => {
    let newIndex = index;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      newIndex = (index + 1) % items.length;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      newIndex = (index - 1 + items.length) % items.length;
    } else {
      return;
    }

    const newTab = items[newIndex];
    if (newTab && !newTab.disabled) {
      handleTabChange(newTab.id);
      const buttons = tabListRef.current?.querySelectorAll('button');
      buttons?.[newIndex]?.focus();
    }
  };

  const activeContent = items.find((item) => item.id === selectedId)?.content;

  return (
    <div className={cx(styles.container, className)} {...props}>
      <div
        ref={tabListRef}
        role="tablist"
        aria-orientation="horizontal"
        className={styles.tabList}
      >
        {items.map((item, index) => {
          const isSelected = item.id === selectedId;
          return (
            <button
              key={item.id}
              role="tab"
              aria-selected={isSelected}
              aria-controls={`panel-${item.id}`}
              id={`tab-${item.id}`}
              tabIndex={isSelected ? 0 : -1}
              disabled={item.disabled}
              className={cx(
                styles.tab,
                isSelected && styles.selected,
                item.disabled && styles.disabled
              )}
              onClick={() => !item.disabled && handleTabChange(item.id)}
              onKeyDown={(e) => handleKeyDown(e, index)}
            >
              {item.label}
            </button>
          );
        })}
      </div>
      <div
        role="tabpanel"
        id={`panel-${selectedId}`}
        aria-labelledby={`tab-${selectedId}`}
        className={styles.tabPanel}
        tabIndex={0}
      >
        {activeContent}
      </div>
    </div>
  );
}
