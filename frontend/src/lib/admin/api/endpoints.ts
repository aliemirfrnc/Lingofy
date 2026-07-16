import { adminApiClient } from './client';

export interface CursorResponse<T> {
  data: T[];
  cursor: string | null;
  next_cursor: string | null;
  previous_cursor: string | null;
  limit: number;
  total_count: number;
}

export interface SuccessResponse<T> {
  data: T;
  meta?: unknown;
}

// Phase 3: Dashboard API Wrapper
export const fetchDashboardOverview = async (): Promise<SuccessResponse<unknown>> => {
  const { data } = await adminApiClient.get('/dashboard');
  return data;
};

// Phase 4: Metrics API Wrapper
export const fetchMetrics = async (): Promise<SuccessResponse<unknown>> => {
  const { data } = await adminApiClient.get('/metrics');
  return data;
};

// Phase 5: Health API Wrapper
export const fetchHealth = async (): Promise<SuccessResponse<unknown>> => {
  const { data } = await adminApiClient.get('/health');
  return data;
};

// Phase 6: Queue API Wrapper
export const fetchQueue = async (cursor?: string, limit = 50): Promise<CursorResponse<unknown>> => {
  const { data } = await adminApiClient.get('/queue', { params: { cursor, limit } });
  return data;
};

// ... other endpoints follow the same pattern
