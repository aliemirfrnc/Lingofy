'use client';

export default function SettingsError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '800px', margin: '0 auto' }}>
      <div role="alert" style={{ color: 'var(--color-danger)' }}>
        <h2>Something went wrong!</h2>
        <p>Failed to load settings.</p>
        <button onClick={() => reset()}>Try again</button>
      </div>
    </div>
  );
}
