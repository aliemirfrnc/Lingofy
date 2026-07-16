'use client';

import { AuthenticatedOnly } from '@/providers/AuthProvider';
import { useDashboardStats } from '@/features/dashboard';
import { DailyGoalWidget, XPWidget, AchievementWidget, WeeklyProgressWidget, UsageWidget } from '@/features/dashboard';
import { LoadingState } from '@/components/app/LoadingState';
import { ErrorState } from '@/components/app/ErrorState';


export default function DashboardPage() {
  const { data: stats, isLoading, isError, error, refetch } = useDashboardStats();

  return (
    <AuthenticatedOnly>
      <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        <h1 style={{ fontFamily: 'var(--font-family-base)', fontSize: 'var(--font-size-2xl)', color: 'var(--color-text-primary)', margin: 0 }}>
          Dashboard
        </h1>

        {isLoading && <LoadingState message="Loading your progress..." />}
        
        {isError && (
          <ErrorState 
            message={error?.message || 'Failed to load dashboard statistics.'}
            onRetry={() => refetch()}
          />
        )}

        {stats && (
          <>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: 'var(--space-6)' 
            }}>
              <DailyGoalWidget goal={stats.dailyGoal} />
              <XPWidget xp={stats.totalXp} level={stats.currentLevel} />
              <AchievementWidget badges={stats.badges} />
              <WeeklyProgressWidget history={stats.history} />
              <UsageWidget />
            </div>
          </>
        )}
      </div>
    </AuthenticatedOnly>
  );
}
