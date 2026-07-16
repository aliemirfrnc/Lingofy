'use client';

import { useContext } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { LocaleContext } from '@/providers/LocaleProvider';
import { ThemeContext } from '@/providers/ThemeProvider';
import styles from './PlatformFoundationView.module.css';

export function PlatformFoundationContext() {
  useQueryClient();

  const { locale } = useContext(LocaleContext);
  const { theme } = useContext(ThemeContext);

  return (
    <p className={styles.context}>
      {locale} · {theme}
    </p>
  );
}
