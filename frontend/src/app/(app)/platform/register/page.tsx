import { RegisterForm } from '@/features/auth';
import { GuestOnly } from '@/providers/AuthProvider';
import Link from 'next/link';

export const metadata = {
  title: 'Register | Customer Platform',
};

export default function RegisterPage() {
  return (
    <GuestOnly>
      <div style={{ padding: 'var(--space-8) var(--space-4)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h1 style={{ fontFamily: 'var(--font-family-base)', fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--space-6)', color: 'var(--color-text-primary)' }}>
          Create an Account
        </h1>
        <RegisterForm />
        <p style={{ marginTop: 'var(--space-6)', fontFamily: 'var(--font-family-base)', color: 'var(--color-text-secondary)' }}>
          Already have an account?{' '}
          <Link href="/platform/login" style={{ color: 'var(--color-brand-primary)', textDecoration: 'none', fontWeight: 'var(--font-weight-medium)' }}>
            Log in
          </Link>
        </p>
      </div>
    </GuestOnly>
  );
}
