import { z } from 'zod';

export const updateProfileSchema = z.object({
  displayName: z.string().min(1, 'Display name is required').max(50, 'Display name must be less than 50 characters').trim()
});

export type UpdateProfileFormData = z.infer<typeof updateProfileSchema>;

export const updatePreferencesSchema = z.object({
  theme: z.enum(['light', 'dark', 'system']).optional(),
  interfaceLanguage: z.string().optional(),
  targetLanguage: z.string().optional(),
  dailyGoalMinutes: z.number().min(5, 'Minimum 5 minutes').max(240, 'Maximum 240 minutes').optional(),
  timezone: z.string().optional(),
  emailNotifications: z.boolean().optional(),
  pushNotifications: z.boolean().optional(),
  marketingEmails: z.boolean().optional()
});

export type UpdatePreferencesFormData = z.infer<typeof updatePreferencesSchema>;
