import {
  NotificationDTO,
  NotificationEvent,
  JobProgressDTO,
  JobProgressEvent,
  JobCompletedDTO,
  JobCompletedEvent,
  JobFailedDTO,
  JobFailedEvent,
  AIStreamDTO,
  AIStreamEvent,
  SubscriptionUpdatedDTO,
  SubscriptionUpdatedEvent,
  ProfileUpdatedDTO,
  ProfileUpdatedEvent
} from '../models/realtimeModels';

export const mapNotificationDTOToEvent = (dto: NotificationDTO): NotificationEvent => ({
  title: dto.title,
  message: dto.message,
  level: dto.level,
  actionUrl: dto.action_url,
});

export const mapJobProgressDTOToEvent = (dto: JobProgressDTO): JobProgressEvent => ({
  jobId: dto.job_id,
  progress: dto.progress,
  label: dto.label,
});

export const mapJobCompletedDTOToEvent = (dto: JobCompletedDTO): JobCompletedEvent => ({
  jobId: dto.job_id,
  result: dto.result,
});

export const mapJobFailedDTOToEvent = (dto: JobFailedDTO): JobFailedEvent => ({
  jobId: dto.job_id,
  reason: dto.reason,
});

export const mapAIStreamDTOToEvent = (dto: AIStreamDTO): AIStreamEvent => ({
  chunk: dto.chunk,
  jobId: dto.job_id,
});

export const mapSubscriptionUpdatedDTOToEvent = (dto: SubscriptionUpdatedDTO): SubscriptionUpdatedEvent => ({
  planName: dto.plan_name,
  status: dto.status,
  updatedField: dto.updated_field,
});

export const mapProfileUpdatedDTOToEvent = (dto: ProfileUpdatedDTO): ProfileUpdatedEvent => ({
  updatedField: dto.updated_field,
});
