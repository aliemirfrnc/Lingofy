import { LoginForm } from '@/features/auth';
import { GuestOnly } from '@/providers/AuthProvider';
import Link from 'next/link';

export const metadata = {
  title: 'Log In | Customer Platform',
};

export default function LoginPage() {
  return (
    <GuestOnly>
      <div style={{ padding: 'var(--space-8) var(--space-4)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h1 style={{ fontFamily: 'var(--font-family-base)', fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--space-6)', color: 'var(--color-text-primary)' }}>
          Welcome Back
        </h1>
        <LoginForm />
        <p style={{ marginTop: 'var(--space-6)', fontFamily: 'var(--font-family-base)', color: 'var(--color-text-secondary)' }}>
          Don&apos;t have an account?{' '}
          <Link href="/platform/register" style={{ color: 'var(--color-brand-primary)', textDecoration: 'none', fontWeight: 'var(--font-weight-medium)' }}>
            Sign up
          </Link>
        </p>
      </div>
    </GuestOnly>
  );
}
