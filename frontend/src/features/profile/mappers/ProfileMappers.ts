import {
  UserProfileDTO,
  UserPreferencesDTO,
  UserSessionDTO,
  SupportedLanguageDTO,
  UpdateProfileRequestDTO,
  UpdatePreferencesRequestDTO
} from '../types';
import {
  UserProfile,
  UserPreferences,
  UserSession,
  SupportedLanguage,
  UpdateProfileRequest,
  UpdatePreferencesRequest
} from '../models/ProfileModels';

export const mapProfileDTOToDomain = (dto: UserProfileDTO): UserProfile => ({
  id: dto.id,
  email: dto.email,
  displayName: dto.display_name,
  role: dto.role,
  createdAt: new Date(dto.created_at)
});

export const mapProfileDomainToDTO = (domain: UpdateProfileRequest): UpdateProfileRequestDTO => ({
  display_name: domain.displayName
});

export const mapPreferencesDTOToDomain = (dto: UserPreferencesDTO): UserPreferences => ({
  theme: dto.theme,
  interfaceLanguage: dto.interface_language,
  targetLanguage: dto.target_language,
  dailyGoalMinutes: dto.daily_goal_minutes,
  timezone: dto.timezone,
  emailNotifications: dto.email_notifications,
  pushNotifications: dto.push_notifications,
  marketingEmails: dto.marketing_emails
});

export const mapPreferencesDomainToDTO = (domain: UpdatePreferencesRequest): UpdatePreferencesRequestDTO => {
  const dto: UpdatePreferencesRequestDTO = {};
  if (domain.theme !== undefined) dto.theme = domain.theme;
  if (domain.interfaceLanguage !== undefined) dto.interface_language = domain.interfaceLanguage;
  if (domain.targetLanguage !== undefined) dto.target_language = domain.targetLanguage;
  if (domain.dailyGoalMinutes !== undefined) dto.daily_goal_minutes = domain.dailyGoalMinutes;
  if (domain.timezone !== undefined) dto.timezone = domain.timezone;
  if (domain.emailNotifications !== undefined) dto.email_notifications = domain.emailNotifications;
  if (domain.pushNotifications !== undefined) dto.push_notifications = domain.pushNotifications;
  if (domain.marketingEmails !== undefined) dto.marketing_emails = domain.marketingEmails;
  return dto;
};

export const mapSessionDTOToDomain = (dto: UserSessionDTO): UserSession => ({
  sessionId: dto.session_id,
  createdAt: new Date(dto.created_at),
  expiresAt: new Date(dto.expires_at)
});

export const mapLanguageDTOToDomain = (dto: SupportedLanguageDTO): SupportedLanguage => ({
  code: dto.code,
  name: dto.name
});
