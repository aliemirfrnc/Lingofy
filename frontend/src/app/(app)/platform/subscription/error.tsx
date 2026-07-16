'use client';

export default function SubscriptionError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '1000px', margin: '0 auto' }}>
      <div role="alert" style={{ color: 'var(--color-danger)' }}>
        <h2>Something went wrong!</h2>
        <p>Failed to load subscription page.</p>
        <button onClick={() => reset()}>Try again</button>
      </div>
    </div>
  );
}
