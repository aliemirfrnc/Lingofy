'use client';

import { ErrorState } from '@/components/app/ErrorState';

export default function AiChatError({
  reset,
}: {
  reset: () => void;
}) {
  return (
    <div style={{ padding: 'var(--spacing-xl) 0', height: 'calc(100vh - 120px)' }}>
      <ErrorState 
        message="Yapay zeka asistanı yüklenirken bir hata oluştu." 
        onRetry={reset}
      />
    </div>
  );
}
