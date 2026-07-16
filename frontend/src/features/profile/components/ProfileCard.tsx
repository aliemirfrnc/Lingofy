'use client';

import { useProfile } from '../hooks/profileHooks';
import styles from './ProfileCard.module.css';

export function ProfileCard() {
  const { data: profile, isLoading, isError, error } = useProfile();

  if (isLoading) {
    return <div className={styles.loading} role="status" aria-live="polite">Loading profile...</div>;
  }

  if (isError || !profile) {
    const errorMessage = error?.message || 'Failed to load profile';
    return (
      <div className={styles.error} role="alert">
        {errorMessage}
      </div>
    );
  }

  return (
    <div className={styles.card}>
      <h2 className={styles.title}>Profile Information</h2>
      <div className={styles.infoGroup}>
        <span className={styles.label}>Name:</span>
        <span className={styles.value}>{profile.displayName}</span>
      </div>
      <div className={styles.infoGroup}>
        <span className={styles.label}>Email:</span>
        <span className={styles.value}>{profile.email}</span>
      </div>
      <div className={styles.infoGroup}>
        <span className={styles.label}>Role:</span>
        <span className={styles.value}>{profile.role}</span>
      </div>
      <div className={styles.infoGroup}>
        <span className={styles.label}>Member Since:</span>
        <span className={styles.value}>{profile.createdAt.toLocaleDateString()}</span>
      </div>
    </div>
  );
}
