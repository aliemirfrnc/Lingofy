'use client';

import { useInvoices } from '../hooks/subscriptionHooks';
import { MaintenanceCard } from './MaintenanceCard';
import styles from './Subscription.module.css';

export function InvoiceTable() {
  const { data: invoices, isLoading, isError, error } = useInvoices();

  if (isLoading) {
    return <section className={styles.card} role="status" aria-live="polite">Loading invoices...</section>;
  }

  if (isError || !invoices) {
    if (error?.type === 'Maintenance') {
      return <MaintenanceCard title="Invoices" error={error} />;
    }
    return (
      <section className={styles.card} role="alert">
        <div className={styles.errorAlert}>{error?.message || 'Failed to load invoices'}</div>
      </section>
    );
  }

  if (invoices.length === 0) {
    return (
      <section className={styles.card} aria-labelledby="invoices-title">
        <h2 id="invoices-title" className={styles.title}>Invoices</h2>
        <p style={{ color: 'var(--color-text-secondary)' }}>No invoices found.</p>
      </section>
    );
  }

  return (
    <section className={styles.card} aria-labelledby="invoices-title">
      <h2 id="invoices-title" className={styles.title}>Invoices</h2>
      
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Amount</th>
              <th scope="col">Status</th>
              <th scope="col">Invoice ID</th>
              <th scope="col">Provider</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map(invoice => (
              <tr key={invoice.id}>
                <td>{invoice.createdAt.toLocaleDateString()}</td>
                <td>{invoice.amount} {invoice.currency}</td>
                <td>{invoice.status}</td>
                <td style={{ fontFamily: 'monospace' }}>{invoice.invoiceId}</td>
                <td>{invoice.provider}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
