import '@/styles/tokens.css';
import { ReactNode } from 'react';
import { AppProviders } from '@/providers/AppProviders';

export const metadata = {
  title: 'Lingofy Dashboard',
  description: 'Your Customer Experience Platform',
};

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="customer-app-root">
      <AppProviders>
        {children}
      </AppProviders>
    </div>
  );
}
