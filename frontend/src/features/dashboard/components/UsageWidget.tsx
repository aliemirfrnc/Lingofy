'use client';

import { useUsage } from '@/features/subscription';
import { MaintenanceCard } from '@/features/subscription';
import { ErrorState } from '@/components/app/ErrorState';

export function UsageWidget() {
  const { data: usage, isLoading, isError, error, refetch } = useUsage();

  if (isLoading) {
    return (
      <div style={{ padding: 'var(--space-4)', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }} role="status">
        Loading usage limits...
      </div>
    );
  }

  if (isError || !usage) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Usage Limits" error={error} />;
    }
    return (
      <div style={{ padding: 'var(--space-4)', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
        <ErrorState message={error?.message || 'Failed to load usage'} onRetry={() => refetch()} />
      </div>
    );
  }

  const renderSimpleProgress = (name: string, used: number, limit: number) => {
    const percentage = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
    const isUnlimited = limit > 999990;
    
    return (
      <div key={name} style={{ marginBottom: 'var(--space-2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-1)' }}>
          <span style={{ fontWeight: 500 }}>{name}</span>
          <span style={{ color: 'var(--color-text-secondary)' }}>{used} / {isUnlimited ? '∞' : limit}</span>
        </div>
        {!isUnlimited && (
          <div style={{ height: '6px', backgroundColor: 'var(--color-border)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ 
              height: '100%', 
              backgroundColor: percentage >= 90 ? 'var(--color-danger)' : 'var(--color-primary)', 
              width: `${percentage}%`,
              transition: 'width 0.3s ease'
            }} />
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: 'var(--space-4)', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }} aria-labelledby="usage-widget-title">
      <h3 id="usage-widget-title" style={{ margin: '0 0 var(--space-4) 0', fontSize: 'var(--text-lg)', fontWeight: 600 }}>Usage Limits</h3>
      <div>
        {renderSimpleProgress('Songs', usage.songs.today, usage.songs.planLimit)}
        {renderSimpleProgress('Words', usage.words.today, usage.words.planLimit)}
        {renderSimpleProgress('AI Messages', usage.aiMessages.today, usage.aiMessages.planLimit)}
      </div>
    </div>
  );
}
