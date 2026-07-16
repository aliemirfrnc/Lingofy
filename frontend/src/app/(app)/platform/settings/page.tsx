'use client';

import { AuthenticatedOnly } from '@/providers/AuthProvider';
import { PreferenceForm } from '@/features/profile';

export default function SettingsPage() {
  return (
    <AuthenticatedOnly>
      <div style={{ padding: 'var(--space-6)', maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ fontFamily: 'var(--font-family-base)', color: 'var(--color-text-primary)', marginBottom: 'var(--spacing-lg)' }}>Settings</h1>
        <PreferenceForm />
      </div>
    </AuthenticatedOnly>
  );
}
