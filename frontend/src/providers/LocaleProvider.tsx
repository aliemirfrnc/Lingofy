'use client';

import { ReactNode, createContext, useMemo } from 'react';

export const DEFAULT_LOCALE = 'tr-TR';

interface LocaleContextValue {
  locale: string;
}

export const LocaleContext = createContext<LocaleContextValue>({
  locale: DEFAULT_LOCALE,
});

interface LocaleProviderProps {
  children: ReactNode;
}

export function LocaleProvider({ children }: LocaleProviderProps) {
  const value = useMemo(() => ({ locale: DEFAULT_LOCALE }), []);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}
