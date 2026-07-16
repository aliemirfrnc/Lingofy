'use client';

import { useUsage } from '../hooks/subscriptionHooks';
import { MaintenanceCard } from './MaintenanceCard';
import styles from './Subscription.module.css';

export function UsageCard() {
  const { data: usage, isLoading, isError, error } = useUsage();

  if (isLoading) {
    return <section className={styles.card} role="status" aria-live="polite">Loading usage details...</section>;
  }

  if (isError || !usage) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Usage Limits" error={error} />;
    }
    return (
      <section className={styles.card} role="alert">
        <div className={styles.errorAlert}>{error?.message || 'Failed to load usage'}</div>
      </section>
    );
  }

  const renderProgress = (name: string, used: number, limit: number) => {
    const percentage = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
    const isUnlimited = limit > 999990;
    
    return (
      <div key={name} className={styles.usageItem}>
        <div className={styles.usageHeader}>
          <span className={styles.usageName}>{name}</span>
          <span className={styles.usageText}>
            {used} / {isUnlimited ? '∞' : limit}
          </span>
        </div>
        {!isUnlimited && (
          <div className={styles.progressBarBg}>
            <div 
              className={styles.progressBarFill} 
              style={{ width: `${percentage}%`, backgroundColor: percentage >= 90 ? 'var(--color-danger)' : 'var(--color-primary)' }}
            />
          </div>
        )}
      </div>
    );
  };

  return (
    <section className={styles.card} aria-labelledby="usage-title">
      <h2 id="usage-title" className={styles.title}>Usage Limits (Today)</h2>
      <div className={styles.usageList}>
        {renderProgress('Songs', usage.songs.today, usage.songs.planLimit)}
        {renderProgress('Words', usage.words.today, usage.words.planLimit)}
        {renderProgress('AI Messages', usage.aiMessages.today, usage.aiMessages.planLimit)}
        {renderProgress('Pronunciation', usage.pronunciation.today, usage.pronunciation.planLimit)}
        {renderProgress('Shadowing (Mins)', usage.shadowingMinutes.today, usage.shadowingMinutes.planLimit)}
      </div>
    </section>
  );
}
