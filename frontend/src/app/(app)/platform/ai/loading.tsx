import { LoadingState } from '@/components/app/LoadingState';

export default function AiChatLoading() {
  return (
    <div style={{ padding: 'var(--spacing-xl) 0', height: 'calc(100vh - 120px)' }}>
      <LoadingState message="Loading AI Workspace..." />
    </div>
  );
}
