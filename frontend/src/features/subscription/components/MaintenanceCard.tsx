'use client';

import styles from './Subscription.module.css';
import { SubscriptionError } from '../models/SubscriptionModels';

interface MaintenanceCardProps {
  title?: string;
  error?: SubscriptionError | Error | null;
}

export function MaintenanceCard({ title = 'Maintenance', error }: MaintenanceCardProps) {
  // Extract detail message from RFC7807 if available
  const message = error instanceof SubscriptionError 
    ? error.message 
    : 'This feature is currently undergoing maintenance and will be available soon.';

  return (
    <section className={styles.card} aria-labelledby="maintenance-title">
      <h2 id="maintenance-title" className={styles.title}>{title}</h2>
      <div className={styles.maintenanceAlert} role="alert">
        <span className={styles.maintenanceIcon}>🚧</span>
        <div>
          <strong>Coming Soon</strong>
          <p>{message}</p>
        </div>
      </div>
    </section>
  );
}
