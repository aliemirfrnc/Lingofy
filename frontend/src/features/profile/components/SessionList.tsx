'use client';

import { useSessions, useRevokeSession, useRevokeOtherSessions } from '../hooks/profileHooks';
import styles from './SessionList.module.css';

export function SessionList() {
  const { data: sessions, isLoading, isError, error } = useSessions();
  const revokeSessionMutation = useRevokeSession();
  const revokeOthersMutation = useRevokeOtherSessions();

  if (isLoading) {
    return <div className={styles.loading} role="status" aria-live="polite">Loading sessions...</div>;
  }

  if (isError || !sessions) {
    return (
      <div className={styles.error} role="alert">
        {error?.message || 'Failed to load sessions'}
      </div>
    );
  }

  if (sessions.length === 0) {
    return <div className={styles.empty}>No active sessions found.</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Active Sessions</h2>
        <button 
          className={styles.revokeAllButton}
          onClick={() => revokeOthersMutation.mutate()}
          disabled={revokeOthersMutation.isPending}
          aria-busy={revokeOthersMutation.isPending}
        >
          {revokeOthersMutation.isPending ? 'Revoking...' : 'Revoke Other Sessions'}
        </button>
      </div>

      <div className={styles.list}>
        {sessions.map(session => (
          <div key={session.sessionId} className={styles.card}>
            <div className={styles.details}>
              <div><strong>Started:</strong> {session.createdAt.toLocaleString()}</div>
              <div><strong>Expires:</strong> {session.expiresAt.toLocaleString()}</div>
              <div className={styles.id}>ID: {session.sessionId.substring(0, 8)}...</div>
            </div>
            <button 
              className={styles.revokeButton}
              onClick={() => revokeSessionMutation.mutate(session.sessionId)}
              disabled={revokeSessionMutation.isPending}
              aria-label={`Revoke session starting with ${session.sessionId.substring(0, 8)}`}
            >
              Revoke
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
