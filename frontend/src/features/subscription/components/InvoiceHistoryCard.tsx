'use client';

import { useHistory } from '../hooks/subscriptionHooks';
import { MaintenanceCard } from './MaintenanceCard';
import styles from './Subscription.module.css';

export function InvoiceHistoryCard() {
  const { data: history, isLoading, isError, error } = useHistory();

  if (isLoading) {
    return <section className={styles.card} role="status" aria-live="polite">Loading subscription history...</section>;
  }

  if (isError || !history) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Subscription History" error={error} />;
    }
    return (
      <section className={styles.card} role="alert">
        <div className={styles.errorAlert}>{error?.message || 'Failed to load history'}</div>
      </section>
    );
  }

  if (history.length === 0) {
    return (
      <section className={styles.card} aria-labelledby="history-title">
        <h2 id="history-title" className={styles.title}>Subscription History</h2>
        <p style={{ color: 'var(--color-text-secondary)' }}>No subscription history found.</p>
      </section>
    );
  }

  return (
    <section className={styles.card} aria-labelledby="history-title">
      <h2 id="history-title" className={styles.title}>Subscription History</h2>
      
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Plan</th>
              <th scope="col">Started At</th>
              <th scope="col">Expires At</th>
              <th scope="col">Status</th>
              <th scope="col">Provider</th>
            </tr>
          </thead>
          <tbody>
            {history.map(item => (
              <tr key={item.id}>
                <td>{item.planName}</td>
                <td>{item.startedAt.toLocaleDateString()}</td>
                <td>{item.expiresAt.toLocaleDateString()}</td>
                <td>{item.status}</td>
                <td>{item.provider}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
