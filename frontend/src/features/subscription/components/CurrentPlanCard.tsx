'use client';

import { useSubscription, useUpgrade } from '../hooks/subscriptionHooks';
import { MaintenanceCard } from './MaintenanceCard';
import styles from './Subscription.module.css';

export function CurrentPlanCard() {
  const { data: currentPlan, isLoading, isError, error } = useSubscription();
  const upgradeMutation = useUpgrade();

  if (isLoading) {
    return <section className={styles.card} role="status" aria-live="polite">Loading plan details...</section>;
  }

  if (isError || !currentPlan) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Current Plan" error={error} />;
    }
    return (
      <section className={styles.card} role="alert">
        <div className={styles.errorAlert}>{error?.message || 'Failed to load plan'}</div>
      </section>
    );
  }

  const handleUpgrade = () => {
    // Calling the API which is expected to return 503 Maintenance in production
    upgradeMutation.mutate({ planName: 'PRO', paymentMethodId: 'mock' });
  };

  return (
    <section className={styles.card} aria-labelledby="plan-title">
      <h2 id="plan-title" className={styles.title}>Current Plan</h2>
      
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

      <div className={styles.detailsGrid}>
        <div className={styles.detailItem}>
          <span className={styles.label}>Plan Name</span>
          <span className={styles.value}>{currentPlan.planName}</span>
        </div>
        <div className={styles.detailItem}>
          <span className={styles.label}>Price</span>
          <span className={styles.value}>{currentPlan.price > 0 ? `${currentPlan.price} ${currentPlan.currency}` : 'Free'}</span>
        </div>
        <div className={styles.detailItem}>
          <span className={styles.label}>Status</span>
          <span className={styles.value}>{currentPlan.status || 'Active'}</span>
        </div>
        {currentPlan.expiresAt && (
          <div className={styles.detailItem}>
            <span className={styles.label}>Renews On</span>
            <span className={styles.value}>{currentPlan.expiresAt.toLocaleDateString()}</span>
          </div>
        )}
      </div>

      <div className={styles.actions}>
        <button 
          className={styles.buttonPrimary} 
          onClick={handleUpgrade}
          disabled={upgradeMutation.isPending}
          aria-busy={upgradeMutation.isPending}
        >
          {upgradeMutation.isPending ? 'Processing...' : 'Upgrade Plan'}
        </button>
      </div>
    </section>
  );
}
