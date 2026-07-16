import Link from 'next/link';

export default function SettingsNotFound() {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Not Found</h2>
      <p>Could not find the settings page.</p>
      <Link href="/platform/dashboard">Return to Dashboard</Link>
    </div>
  );
}
