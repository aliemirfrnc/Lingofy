import { apiClient } from '@/lib/app/api/client';
import {
  UserProfileDTO,
  UserPreferencesDTO,
  UserSessionDTO,
  SupportedLanguageDTO,
  UpdateProfileRequestDTO,
  UpdatePreferencesRequestDTO,
  RevokeSessionResponseDTO,
  RevokeOthersResponseDTO
} from '../types';

export const getProfile = async (): Promise<UserProfileDTO> => {
  const { data } = await apiClient.get<UserProfileDTO>('/me');
  return data;
};

export const updateProfile = async (req: UpdateProfileRequestDTO): Promise<UserProfileDTO> => {
  const { data } = await apiClient.patch<UserProfileDTO>('/me', req);
  return data;
};

export const getPreferences = async (): Promise<UserPreferencesDTO> => {
  const { data } = await apiClient.get<UserPreferencesDTO>('/me/preferences');
  return data;
};

export const updatePreferences = async (req: UpdatePreferencesRequestDTO): Promise<UserPreferencesDTO> => {
  const { data } = await apiClient.patch<UserPreferencesDTO>('/me/preferences', req);
  return data;
};

export const getSessions = async (): Promise<UserSessionDTO[]> => {
  const { data } = await apiClient.get<UserSessionDTO[]>('/me/sessions');
  return data;
};

export const revokeSession = async (sessionId: string): Promise<RevokeSessionResponseDTO> => {
  const { data } = await apiClient.delete<RevokeSessionResponseDTO>(`/me/sessions/${sessionId}`);
  return data;
};

export const revokeOtherSessions = async (): Promise<RevokeOthersResponseDTO> => {
  const { data } = await apiClient.delete<RevokeOthersResponseDTO>('/me/sessions/others');
  return data;
};

export const getLanguages = async (): Promise<SupportedLanguageDTO[]> => {
  const { data } = await apiClient.get<SupportedLanguageDTO[]>('/me/languages');
  return data;
};
