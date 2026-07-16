export interface UserProfile {
  id: number;
  email: string;
  displayName: string;
  role: string;
  createdAt: Date;
}

export interface UpdateProfileRequest {
  displayName: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  interfaceLanguage: string;
  targetLanguage: string;
  dailyGoalMinutes: number;
  timezone: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
  marketingEmails: boolean;
}

export type UpdatePreferencesRequest = Partial<UserPreferences>;

export interface UserSession {
  sessionId: string;
  createdAt: Date;
  expiresAt: Date;
}

export interface SupportedLanguage {
  code: string;
  name: string;
}
