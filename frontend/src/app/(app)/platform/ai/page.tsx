'use client';

import { ChatLayout } from '@/features/ai-chat';
import { AuthenticatedOnly } from '@/providers/AuthProvider';

export default function AiChatPage() {
  return (
    <AuthenticatedOnly>
      <div style={{ padding: 'var(--spacing-md) 0' }}>
        <h1 style={{ marginBottom: 'var(--spacing-md)', fontSize: 'var(--text-xl)', fontWeight: 600 }}>AI Mentor</h1>
        <ChatLayout />
      </div>
    </AuthenticatedOnly>
  );
}
