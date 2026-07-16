import Link from 'next/link';

export default function AiChatNotFound() {
  return (
    <div style={{ padding: 'var(--spacing-xl) 0', textAlign: 'center' }}>
      <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--spacing-sm)' }}>Asistan Bulunamadı</h2>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-lg)' }}>
        Aradığınız yapay zeka çalışma alanı mevcut değil.
      </p>
      <Link href="/platform" style={{ color: 'var(--color-primary)', textDecoration: 'none', fontWeight: 500 }}>
        Platforma Dön
      </Link>
    </div>
  );
}
