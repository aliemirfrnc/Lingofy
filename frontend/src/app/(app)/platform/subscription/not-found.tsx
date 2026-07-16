import Link from 'next/link';

export default function SubscriptionNotFound() {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Not Found</h2>
      <p>Could not find the subscription page.</p>
      <Link href="/platform/dashboard">Return to Dashboard</Link>
    </div>
  );
}
