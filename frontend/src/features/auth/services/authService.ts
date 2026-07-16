import { apiClient } from '@/lib/app/api/client';
import { LoginRequest, RegisterRequest } from '../models/authModels';

// Using raw backend DTO types internally, returning them to be mapped by mappers.
export interface AuthResponseDTO {
  status: string;
  email: string;
  message: string;
}

export interface MeResponseDTO {
  email: string;
}

export const authService = {
  login: async (data: LoginRequest): Promise<AuthResponseDTO> => {
    const response = await apiClient.post<AuthResponseDTO>('/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponseDTO> => {
    const response = await apiClient.post<AuthResponseDTO>('/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  logoutAll: async (): Promise<void> => {
    await apiClient.post('/auth/logout-all');
  },

  refresh: async (): Promise<AuthResponseDTO> => {
    const response = await apiClient.post<AuthResponseDTO>('/auth/refresh');
    return response.data;
  },

  me: async (): Promise<MeResponseDTO> => {
    const response = await apiClient.get<MeResponseDTO>('/auth/me');
    return response.data;
  },
};
