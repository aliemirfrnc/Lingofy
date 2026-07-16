import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import { authService } from '../services/authService';
import { mapAuthResponseToDomain, mapMeResponseToUser } from '../mappers/authMappers';
import { LoginRequest, RegisterRequest } from '../models/authModels';

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const response = await authService.login(data);
      return mapAuthResponseToDomain(response);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth() });
    },
    retry: false, // Explicit rule: POST mutation retry etmeyecek.
  });
}

export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      const response = await authService.register(data);
      return mapAuthResponseToDomain(response);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth() });
    },
    retry: false,
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await authService.logout();
    },
    onSettled: () => {
      queryClient.setQueryData(queryKeys.auth(), null);
      queryClient.clear(); // Clears all queries including dashboard etc on logout
    },
    retry: false,
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.auth(),
    queryFn: async () => {
      const response = await authService.me();
      return mapMeResponseToUser(response);
    },
    retry: false,
  });
}
