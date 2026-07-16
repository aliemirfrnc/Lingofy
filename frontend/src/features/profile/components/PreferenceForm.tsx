'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { usePreferences, useUpdatePreferences, useLanguages } from '../hooks/profileHooks';
import { updatePreferencesSchema, UpdatePreferencesFormData } from '../validation/ProfileValidation';
import styles from './PreferenceForm.module.css';

export function PreferenceForm() {
  const { data: preferences, isLoading: prefsLoading, isError: prefsError } = usePreferences();
  const { data: languages, isLoading: langLoading } = useLanguages();
  const updateMutation = useUpdatePreferences();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty }
  } = useForm<UpdatePreferencesFormData>({
    resolver: zodResolver(updatePreferencesSchema),
    defaultValues: {
      theme: 'system',
      interfaceLanguage: 'en',
      targetLanguage: 'en',
      dailyGoalMinutes: 15,
      emailNotifications: true,
      pushNotifications: false,
      marketingEmails: false,
    }
  });

  useEffect(() => {
    if (preferences) {
      reset({
        theme: preferences.theme,
        interfaceLanguage: preferences.interfaceLanguage,
        targetLanguage: preferences.targetLanguage,
        dailyGoalMinutes: preferences.dailyGoalMinutes,
        emailNotifications: preferences.emailNotifications,
        pushNotifications: preferences.pushNotifications,
        marketingEmails: preferences.marketingEmails,
      });
    }
  }, [preferences, reset]);

  if (prefsLoading || langLoading) {
    return <div className={styles.loading} role="status" aria-live="polite">Loading preferences...</div>;
  }

  if (prefsError) {
    return <div className={styles.error} role="alert">Failed to load preferences</div>;
  }

  const onSubmit = (data: UpdatePreferencesFormData) => {
    updateMutation.mutate(data);
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
      <h2 className={styles.title}>Preferences</h2>
      
      {updateMutation.isError && (
        <div className={styles.error} role="alert">
          {updateMutation.error?.message || 'Failed to update preferences'}
        </div>
      )}

      <div className={styles.fieldGroup}>
        <label htmlFor="theme" className={styles.label}>Theme</label>
        <select 
          id="theme" 
          {...register('theme')} 
          className={styles.select}
          aria-invalid={!!errors.theme}
          aria-describedby={errors.theme ? "theme-error" : undefined}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
        {errors.theme && <span id="theme-error" className={styles.errorText}>{errors.theme.message}</span>}
      </div>

      <div className={styles.fieldGroup}>
        <label htmlFor="interfaceLanguage" className={styles.label}>Interface Language</label>
        <select 
          id="interfaceLanguage" 
          {...register('interfaceLanguage')} 
          className={styles.select}
          aria-invalid={!!errors.interfaceLanguage}
        >
          {languages?.map(lang => (
            <option key={lang.code} value={lang.code}>{lang.name}</option>
          ))}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label htmlFor="targetLanguage" className={styles.label}>Target Language</label>
        <select 
          id="targetLanguage" 
          {...register('targetLanguage')} 
          className={styles.select}
          aria-invalid={!!errors.targetLanguage}
        >
          {languages?.map(lang => (
            <option key={lang.code} value={lang.code}>{lang.name}</option>
          ))}
        </select>
      </div>

      <div className={styles.fieldGroup}>
        <label htmlFor="dailyGoalMinutes" className={styles.label}>Daily Goal (Minutes)</label>
        <input 
          id="dailyGoalMinutes" 
          type="number" 
          {...register('dailyGoalMinutes', { valueAsNumber: true })} 
          className={styles.input}
          aria-invalid={!!errors.dailyGoalMinutes}
          aria-describedby={errors.dailyGoalMinutes ? "dailyGoal-error" : undefined}
        />
        {errors.dailyGoalMinutes && <span id="dailyGoal-error" className={styles.errorText}>{errors.dailyGoalMinutes.message}</span>}
      </div>

      <div className={styles.checkboxGroup}>
        <input 
          id="emailNotifications" 
          type="checkbox" 
          {...register('emailNotifications')} 
          className={styles.checkbox}
        />
        <label htmlFor="emailNotifications">Email Notifications</label>
      </div>

      <div className={styles.checkboxGroup}>
        <input 
          id="pushNotifications" 
          type="checkbox" 
          {...register('pushNotifications')} 
          className={styles.checkbox}
        />
        <label htmlFor="pushNotifications">Push Notifications</label>
      </div>

      <div className={styles.checkboxGroup}>
        <input 
          id="marketingEmails" 
          type="checkbox" 
          {...register('marketingEmails')} 
          className={styles.checkbox}
        />
        <label htmlFor="marketingEmails">Marketing Emails</label>
      </div>

      <button 
        type="submit" 
        className={styles.submitButton} 
        disabled={!isDirty || updateMutation.isPending}
        aria-busy={updateMutation.isPending}
      >
        {updateMutation.isPending ? 'Saving...' : 'Save Preferences'}
      </button>
    </form>
  );
}
