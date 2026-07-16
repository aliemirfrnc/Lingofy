export type ConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'offline' | 'error';

// DTOs (Data Transfer Objects) - What comes from the backend
export interface NotificationDTO {
  title: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  action_url?: string;
}

export interface JobProgressDTO {
  job_id: string;
  progress: number;
  label: string;
}

export interface JobCompletedDTO {
  job_id: string;
  result: Record<string, unknown>;
}

export interface JobFailedDTO {
  job_id: string;
  reason: string;
}

export interface AIStreamDTO {
  chunk: string;
  job_id: string;
}

export interface SubscriptionUpdatedDTO {
  plan_name: string;
  status: string;
  updated_field?: string;
}

export interface ProfileUpdatedDTO {
  updated_field: string;
}

// Domain Models - What the UI uses
export interface NotificationEvent {
  title: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  actionUrl?: string;
}

export interface JobProgressEvent {
  jobId: string;
  progress: number;
  label: string;
}

export interface JobCompletedEvent {
  jobId: string;
  result: Record<string, unknown>;
}

export interface JobFailedEvent {
  jobId: string;
  reason: string;
}

export interface AIStreamEvent {
  chunk: string;
  jobId: string;
}

export interface SubscriptionUpdatedEvent {
  planName: string;
  status: string;
  updatedField?: string;
}

export interface ProfileUpdatedEvent {
  updatedField: string;
}


export type RealtimeEventCallback = (type: string, payload: unknown) => void;
