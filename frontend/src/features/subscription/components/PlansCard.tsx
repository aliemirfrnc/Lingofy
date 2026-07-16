'use client';

import { usePlans, useUpgrade } from '../hooks/subscriptionHooks';
import { MaintenanceCard } from './MaintenanceCard';
import styles from './Subscription.module.css';

export function PlansCard() {
  const { data: plans, isLoading, isError, error } = usePlans();
  const upgradeMutation = useUpgrade();

  if (isLoading) {
    return <section className={styles.card} role="status" aria-live="polite">Loading available plans...</section>;
  }

  if (isError || !plans) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Available Plans" error={error} />;
    }
    return (
      <section className={styles.card} role="alert">
        <div className={styles.errorAlert}>{error?.message || 'Failed to load plans'}</div>
      </section>
    );
  }

  const handleSelectPlan = (planName: string) => {
    upgradeMutation.mutate({ planName, paymentMethodId: 'mock' });
  };

  return (
    <section className={styles.card} aria-labelledby="plans-title">
      <h2 id="plans-title" className={styles.title}>Available Plans</h2>
      
      {upgradeMutation.isError && upgradeMutation.error?.type === 'Maintenance' && (
        <div className={styles.maintenanceAlert} role="alert" style={{ marginBottom: 'var(--spacing-md)' }}>
          <span className={styles.maintenanceIcon}>🚧</span>
          <div>
            <strong>Upgrade Unavailable</strong>
            <p>{upgradeMutation.error.message}</p>
          </div>
        </div>
      )}

      {upgradeMutation.isError && upgradeMutation.error?.type !== 'Maintenance' && (
        <div className={styles.errorAlert} role="alert" style={{ marginBottom: 'var(--spacing-md)' }}>
          {upgradeMutation.error.message}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 'var(--spacing-md)' }}>
        {plans.map(plan => (
          <div key={plan.name} style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: 'var(--spacing-md)' }}>
            <h3 style={{ margin: '0 0 var(--spacing-sm) 0' }}>{plan.name}</h3>
            <p style={{ fontSize: 'var(--text-xl)', fontWeight: 700, margin: '0 0 var(--spacing-md) 0' }}>
              {plan.price > 0 ? `${plan.price} ${plan.currency}` : 'Free'}
            </p>
            <ul style={{ paddingLeft: '20px', margin: '0 0 var(--spacing-md) 0', color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)' }}>
              <li>{plan.limits.songs === 999999 ? 'Unlimited' : plan.limits.songs} songs</li>
              <li>{plan.limits.words === 999999 ? 'Unlimited' : plan.limits.words} words</li>
              <li>{plan.limits.aiMessages === 999999 ? 'Unlimited' : plan.limits.aiMessages} AI messages</li>
            </ul>
            <button 
              className={styles.buttonPrimary} 
              style={{ width: '100%' }}
              onClick={() => handleSelectPlan(plan.name)}
              disabled={upgradeMutation.isPending}
            >
              Select Plan
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
