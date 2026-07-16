'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema } from '../validation/authSchemas';
import { LoginRequest } from '../models/authModels';
import { useLogin } from '../hooks/useAuthMutations';
import { Input } from '@/components/app/Input';
import { Button } from '@/components/app/Button';
import { ErrorState } from '@/components/app/ErrorState';
import styles from './AuthForm.module.css';
import { ApiError } from '@/lib/app/api/client';

export function LoginForm() {
  const { mutate: login, isPending, error } = useLogin();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = (data: LoginRequest) => {
    login(data);
  };

  const errorMessage = error instanceof ApiError ? error.message : error?.message;

  return (
    <div className={styles.container}>
      {error && <ErrorState message={errorMessage || 'An error occurred during login'} />}
      <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register('email')}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register('password')}
        />
        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isPending}
          disabled={isPending}
          className={styles.submitButton}
        >
          Sign In
        </Button>
      </form>
    </div>
  );
}
