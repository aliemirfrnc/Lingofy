'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema } from '../validation/authSchemas';
import { RegisterRequest } from '../models/authModels';
import { useRegister } from '../hooks/useAuthMutations';
import { Input } from '@/components/app/Input';
import { Button } from '@/components/app/Button';
import { ErrorState } from '@/components/app/ErrorState';
import styles from './AuthForm.module.css';
import { ApiError } from '@/lib/app/api/client';

export function RegisterForm() {
  const { mutate: registerUser, isPending, error } = useRegister();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterRequest>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = (data: RegisterRequest) => {
    registerUser(data);
  };

  const errorMessage = error instanceof ApiError ? error.message : error?.message;

  return (
    <div className={styles.container}>
      {error && <ErrorState message={errorMessage || 'An error occurred during registration'} />}
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
          autoComplete="new-password"
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
          Create Account
        </Button>
      </form>
    </div>
  );
}
