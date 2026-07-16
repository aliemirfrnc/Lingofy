'use client';

import { createContext, useContext, ReactNode, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser, User } from '@/features/auth';
import { LoadingState } from '@/components/app/LoadingState';

interface AuthContextValue {
  user: User | null | undefined;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  user: undefined,
  isLoading: true,
  isAuthenticated: false,
});

/**
 * Provides authentication state and manages user session globally.
 * Uses React Query to cache and synchronize user data from the backend.
 * 
 * @param children - React nodes to render inside the provider
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: user, isLoading, isError } = useCurrentUser();

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user && !isError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * A route guard component that restricts access to authenticated users only.
 * If a guest user attempts to access the route, they will be redirected to the platform dashboard.
 * Prevents hydration mismatches by returning a loading state until the query resolves.
 *
 * @param children - The component tree to render if the user is a guest.
 * @param redirectTo - The path to redirect authenticated users to (default: /platform/dashboard).
 */
export function GuestOnly({ children, redirectTo = '/platform/dashboard' }: { children: ReactNode; redirectTo?: string }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace(redirectTo);
    }
  }, [isLoading, isAuthenticated, router, redirectTo]);

  if (isLoading) {
    return <LoadingState message="Yükleniyor..." fullPage />;
  }

  if (isAuthenticated) {
    return null; // Will redirect
  }

  return <>{children}</>;
}

/**
 * A route guard component that restricts access to authenticated users only.
 * If a guest user attempts to access the route, they will be redirected to the login page.
 * Prevents hydration mismatches by returning a loading state until the query resolves.
 *
 * @param children - The component tree to render if the user is authenticated.
 * @param redirectTo - The path to redirect guest users to (default: /platform/login).
 */
export function AuthenticatedOnly({ children, redirectTo = '/platform/login' }: { children: ReactNode; redirectTo?: string }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace(redirectTo);
    }
  }, [isLoading, isAuthenticated, router, redirectTo]);

  if (isLoading) {
    return <LoadingState message="Oturum kontrol ediliyor..." fullPage />;
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return <>{children}</>;
}
