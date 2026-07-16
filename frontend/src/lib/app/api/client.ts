import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// RFC7807 Error Model Wrapper
export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: Record<string, string[]>;
  extensions?: Record<string, unknown>;
}

export class ApiError extends Error {
  public status: number;
  public details: ProblemDetails | null;

  constructor(message: string, status: number, details: ProblemDetails | null = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Crucial for refresh tokens and auth cookies
});

// Interceptor to add correlation IDs or similar tracking mechanisms
apiClient.interceptors.request.use((config) => {
  // In a real app, generate a unique ID, or read from a tracking library
  const requestId = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString();
  config.headers['X-Request-Id'] = requestId;
  config.headers['X-Correlation-Id'] = requestId;
  return config;
});

// Response interceptor to parse RFC7807 and handle common errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ProblemDetails | { detail?: string }>) => {
    if (error.response) {
      const { status, data } = error.response;
      
      let message = 'An unexpected error occurred.';
      let problemDetails: ProblemDetails | null = null;

      if (data && typeof data === 'object') {
        if ('title' in data && 'detail' in data) {
          problemDetails = data as ProblemDetails;
          message = problemDetails.detail || problemDetails.title;
        } else if ('detail' in data) {
          message = data.detail || message;
        }
      }

      return Promise.reject(new ApiError(message, status, problemDetails));
    } else if (error.request) {
      // Network / Offline Error
      const offlineMessage = 'Network error. Please check your internet connection.';
      return Promise.reject(new ApiError(offlineMessage, 0));
    }

    return Promise.reject(new ApiError(error.message, 500));
  }
);
