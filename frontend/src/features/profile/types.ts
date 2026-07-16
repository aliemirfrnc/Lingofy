export interface UserProfileDTO {
  id: number;
  email: string;
  display_name: string;
  role: string;
  created_at: string;
}

export interface UpdateProfileRequestDTO {
  display_name: string;
}

export interface UserPreferencesDTO {
  theme: 'light' | 'dark' | 'system';
  interface_language: string;
  target_language: string;
  daily_goal_minutes: number;
  timezone: string;
  email_notifications: boolean;
  push_notifications: boolean;
  marketing_emails: boolean;
}

export type UpdatePreferencesRequestDTO = Partial<UserPreferencesDTO>;

export interface UserSessionDTO {
  session_id: string;
  created_at: string;
  expires_at: string;
}

export interface RevokeSessionResponseDTO {
  session_id: string;
  status: string;
}

export interface RevokeOthersResponseDTO {
  revoked: number;
  status: string;
}

export interface SupportedLanguageDTO {
  code: string;
  name: string;
}
