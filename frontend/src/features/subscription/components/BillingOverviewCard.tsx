'use client';

import { useBillingOverview } from '../hooks/subscriptionHooks';
import { MaintenanceCard } from './MaintenanceCard';
import styles from './Subscription.module.css';

export function BillingOverviewCard() {
  const { data: billing, isLoading, isError, error } = useBillingOverview();

  if (isLoading) {
    return <section className={styles.card} role="status" aria-live="polite">Loading billing overview...</section>;
  }

  if (isError || !billing) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Billing Overview" error={error} />;
    }
    return (
      <section className={styles.card} role="alert">
        <div className={styles.errorAlert}>{error?.message || 'Failed to load billing overview'}</div>
      </section>
    );
  }

  return (
    <section className={styles.card} aria-labelledby="billing-title">
      <h2 id="billing-title" className={styles.title}>Billing Overview</h2>
      
      <div className={styles.detailsGrid}>
        <div className={styles.detailItem}>
          <span className={styles.label}>Plan</span>
          <span className={styles.value}>{billing.planName}</span>
        </div>
        <div className={styles.detailItem}>
          <span className={styles.label}>Provider</span>
          <span className={styles.value}>{billing.provider || 'N/A'}</span>
        </div>
        <div className={styles.detailItem}>
          <span className={styles.label}>Auto-Renew</span>
          <span className={styles.value}>{billing.cancelAtPeriodEnd ? 'Disabled' : 'Enabled'}</span>
        </div>
      </div>

      {billing.lastPayment && (
        <div style={{ marginTop: 'var(--spacing-md)' }}>
          <h3 style={{ fontSize: 'var(--text-md)', margin: '0 0 var(--spacing-xs) 0', color: 'var(--color-text-secondary)' }}>Last Payment</h3>
          <div className={styles.detailsGrid}>
            <div className={styles.detailItem}>
              <span className={styles.label}>Amount</span>
              <span className={styles.value}>{billing.lastPayment.amount} {billing.lastPayment.currency}</span>
            </div>
            <div className={styles.detailItem}>
              <span className={styles.label}>Date</span>
              <span className={styles.value}>{billing.lastPayment.paidAt.toLocaleDateString()}</span>
            </div>
            <div className={styles.detailItem}>
              <span className={styles.label}>Status</span>
              <span className={styles.value}>{billing.lastPayment.status}</span>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
