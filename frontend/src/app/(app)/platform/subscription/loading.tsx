export default function SubscriptionLoading() {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '1000px', margin: '0 auto' }}>
      <div role="status" aria-live="polite">Loading subscription details...</div>
    </div>
  );
}
