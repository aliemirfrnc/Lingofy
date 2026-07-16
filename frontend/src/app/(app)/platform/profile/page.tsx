'use client';

import { AuthenticatedOnly } from '@/providers/AuthProvider';
import { ProfileCard, SessionList } from '@/features/profile';

export default function ProfilePage() {
  return (
    <AuthenticatedOnly>
      <div style={{ padding: 'var(--space-6)', maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ fontFamily: 'var(--font-family-base)', color: 'var(--color-text-primary)', marginBottom: 'var(--spacing-lg)' }}>Profile</h1>
        <ProfileCard />
        <SessionList />
      </div>
    </AuthenticatedOnly>
  );
}
