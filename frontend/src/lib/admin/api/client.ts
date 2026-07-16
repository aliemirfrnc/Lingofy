import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Phase 16: RFC7807 Error Handling Wrapper
export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: Record<string, string[]>;
}

export const adminApiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_ADMIN_API_URL || '/api/admin/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response Interceptor for generic RFC7807 handling
adminApiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ProblemDetails>) => {
    return Promise.reject(error);
  }
);
