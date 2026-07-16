import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import {
  fetchProfile,
  editProfile,
  fetchPreferences,
  editPreferences,
  fetchSessions,
  terminateSession,
  terminateOtherSessions,
  fetchLanguages
} from '../services/profileApplicationService';
import {
  UserProfile,
  UserPreferences,
  UserSession,
  SupportedLanguage,
  UpdateProfileRequest,
  UpdatePreferencesRequest
} from '../models/ProfileModels';
import { ProfileError } from '../models/ProfileError';

export const useProfile = () => {
  return useQuery<UserProfile, ProfileError>({
    queryKey: queryKeys.profile(),
    queryFn: fetchProfile,
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation<UserProfile, ProfileError, UpdateProfileRequest, { previousProfile?: UserProfile }>({
    mutationFn: editProfile,
    retry: false,
    onMutate: async (newProfile) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.profile() });
      const previousProfile = queryClient.getQueryData<UserProfile>(queryKeys.profile());

      if (previousProfile) {
        queryClient.setQueryData<UserProfile>(queryKeys.profile(), {
          ...previousProfile,
          displayName: newProfile.displayName,
        });
      }

      return { previousProfile };
    },
    onError: (err, newProfile, context) => {
      if (context?.previousProfile) {
        queryClient.setQueryData(queryKeys.profile(), context.previousProfile);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.profile() });
    },
  });
};

export const usePreferences = () => {
  return useQuery<UserPreferences, ProfileError>({
    queryKey: queryKeys.preferences(),
    queryFn: fetchPreferences,
  });
};

export const useUpdatePreferences = () => {
  const queryClient = useQueryClient();

  return useMutation<UserPreferences, ProfileError, UpdatePreferencesRequest, { previousPreferences?: UserPreferences }>({
    mutationFn: editPreferences,
    retry: false,
    onMutate: async (newPreferences) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.preferences() });
      const previousPreferences = queryClient.getQueryData<UserPreferences>(queryKeys.preferences());

      if (previousPreferences) {
        queryClient.setQueryData<UserPreferences>(queryKeys.preferences(), {
          ...previousPreferences,
          ...newPreferences,
        });
      }

      return { previousPreferences };
    },
    onError: (err, newPreferences, context) => {
      if (context?.previousPreferences) {
        queryClient.setQueryData(queryKeys.preferences(), context.previousPreferences);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.preferences() });
    },
  });
};

export const useSessions = () => {
  return useQuery<UserSession[], ProfileError>({
    queryKey: queryKeys.sessions(),
    queryFn: fetchSessions,
  });
};

export const useRevokeSession = () => {
  const queryClient = useQueryClient();

  return useMutation<void, ProfileError, string, { previousSessions?: UserSession[] }>({
    mutationFn: terminateSession,
    retry: false,
    onMutate: async (sessionId) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.sessions() });
      const previousSessions = queryClient.getQueryData<UserSession[]>(queryKeys.sessions());

      if (previousSessions) {
        queryClient.setQueryData<UserSession[]>(
          queryKeys.sessions(),
          previousSessions.filter(s => s.sessionId !== sessionId)
        );
      }

      return { previousSessions };
    },
    onError: (err, sessionId, context) => {
      if (context?.previousSessions) {
        queryClient.setQueryData(queryKeys.sessions(), context.previousSessions);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions() });
    },
  });
};

export const useRevokeOtherSessions = () => {
  const queryClient = useQueryClient();

  return useMutation<number, ProfileError, void, { previousSessions?: UserSession[] }>({
    mutationFn: terminateOtherSessions,
    retry: false,
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: queryKeys.sessions() });
      const previousSessions = queryClient.getQueryData<UserSession[]>(queryKeys.sessions());

      // Optimistic update: Since we can't easily know WHICH session is the current one 
      // without extra backend flags, we might just clear all of them except one.
      // But the safest optimistic update is to just wait for invalidation, 
      // OR we empty the list temporarily if we can't determine current session.
      // The rules state "Current Session backend tarafından işaretlenmiyorsa frontend tahmin yürütmeyecek."
      // So we will NOT optimistically filter the list if we don't know the current session id.
      // We will just return previousSessions for rollback.

      return { previousSessions };
    },
    onError: (err, variables, context) => {
      if (context?.previousSessions) {
        queryClient.setQueryData(queryKeys.sessions(), context.previousSessions);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions() });
    },
  });
};

export const useLanguages = () => {
  return useQuery<SupportedLanguage[], ProfileError>({
    queryKey: queryKeys.languages(),
    queryFn: fetchLanguages,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  });
};
