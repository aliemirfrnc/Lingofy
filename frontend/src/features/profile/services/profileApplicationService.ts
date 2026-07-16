import {
  getProfile,
  updateProfile,
  getPreferences,
  updatePreferences,
  getSessions,
  revokeSession,
  revokeOtherSessions,
  getLanguages
} from './profileApiService';
import {
  mapProfileDTOToDomain,
  mapProfileDomainToDTO,
  mapPreferencesDTOToDomain,
  mapPreferencesDomainToDTO,
  mapSessionDTOToDomain,
  mapLanguageDTOToDomain
} from '../mappers/ProfileMappers';
import {
  UserProfile,
  UserPreferences,
  UserSession,
  SupportedLanguage,
  UpdateProfileRequest,
  UpdatePreferencesRequest
} from '../models/ProfileModels';
import { ProfileError, ProfileErrorType } from '../models/ProfileError';
import { ApiError } from '@/lib/app/api/client';

const handleApiError = (err: unknown): never => {
  if (err instanceof ApiError) {
    let type: ProfileErrorType = 'Unknown';
    if (err.status === 422) type = 'Validation';
    else if (err.status === 401) type = 'Unauthorized';
    else if (err.status === 403) type = 'Forbidden';
    else if (err.status === 503) type = 'Maintenance';
    else if (err.status === 0) type = 'Offline';

    throw new ProfileError(
      err.message,
      type,
      err.details?.errors,
      err.status
    );
  }
  throw new ProfileError('An unexpected error occurred', 'Unknown');
};

export const fetchProfile = async (): Promise<UserProfile> => {
  try {
    const dto = await getProfile();
    return mapProfileDTOToDomain(dto);
  } catch (err) {
    return handleApiError(err);
  }
};

export const editProfile = async (req: UpdateProfileRequest): Promise<UserProfile> => {
  try {
    const dtoReq = mapProfileDomainToDTO(req);
    const dtoRes = await updateProfile(dtoReq);
    return mapProfileDTOToDomain(dtoRes);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchPreferences = async (): Promise<UserPreferences> => {
  try {
    const dto = await getPreferences();
    return mapPreferencesDTOToDomain(dto);
  } catch (err) {
    return handleApiError(err);
  }
};

export const editPreferences = async (req: UpdatePreferencesRequest): Promise<UserPreferences> => {
  try {
    const dtoReq = mapPreferencesDomainToDTO(req);
    const dtoRes = await updatePreferences(dtoReq);
    return mapPreferencesDTOToDomain(dtoRes);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchSessions = async (): Promise<UserSession[]> => {
  try {
    const dtos = await getSessions();
    return dtos.map(mapSessionDTOToDomain);
  } catch (err) {
    return handleApiError(err);
  }
};

export const terminateSession = async (sessionId: string): Promise<void> => {
  try {
    await revokeSession(sessionId);
  } catch (err) {
    return handleApiError(err);
  }
};

export const terminateOtherSessions = async (): Promise<number> => {
  try {
    const res = await revokeOtherSessions();
    return res.revoked;
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchLanguages = async (): Promise<SupportedLanguage[]> => {
  try {
    const dtos = await getLanguages();
    return dtos.map(mapLanguageDTOToDomain);
  } catch (err) {
    return handleApiError(err);
  }
};
