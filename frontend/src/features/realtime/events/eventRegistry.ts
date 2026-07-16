import { QueryClient } from '@tanstack/react-query';
import {
  mapNotificationDTOToEvent,
  mapJobProgressDTOToEvent,
  mapJobCompletedDTOToEvent,
  mapJobFailedDTOToEvent,
  mapAIStreamDTOToEvent,
  mapSubscriptionUpdatedDTOToEvent,
  mapProfileUpdatedDTOToEvent
} from '../mappers/realtimeMappers';
import {
  NotificationDTO, NotificationEvent,
  JobProgressDTO, JobProgressEvent,
  JobCompletedDTO, JobCompletedEvent,
  JobFailedDTO, JobFailedEvent,
  AIStreamDTO, AIStreamEvent,
  SubscriptionUpdatedDTO, SubscriptionUpdatedEvent,
  ProfileUpdatedDTO, ProfileUpdatedEvent
} from '../models/realtimeModels';
import { handleNotification } from './notification';
import { handleJobProgress } from './jobProgress';
import { handleJobCompleted } from './jobCompleted';
import { handleJobFailed } from './jobFailed';
import { handleAIStream } from './aiStream';
import { handleSubscriptionUpdated } from './subscriptionUpdated';
import { handleProfileUpdated } from './profileUpdated';

import { RealtimeEventCallback } from '../models/realtimeModels';

export const processRealtimeEvent = (
  type: string,
  rawData: unknown,
  queryClient: QueryClient,
  broadcastCallback?: RealtimeEventCallback
) => {
  let domainEvent: unknown = null;

  switch (type) {
    case 'notification':
      domainEvent = mapNotificationDTOToEvent(rawData as NotificationDTO);
      handleNotification(domainEvent as NotificationEvent, queryClient);
      break;
    case 'job.progress':
      domainEvent = mapJobProgressDTOToEvent(rawData as JobProgressDTO);
      handleJobProgress(domainEvent as JobProgressEvent);
      break;
    case 'job.completed':
      domainEvent = mapJobCompletedDTOToEvent(rawData as JobCompletedDTO);
      handleJobCompleted(domainEvent as JobCompletedEvent, queryClient);
      break;
    case 'job.failed':
      domainEvent = mapJobFailedDTOToEvent(rawData as JobFailedDTO);
      handleJobFailed(domainEvent as JobFailedEvent);
      break;
    case 'ai.stream':
      domainEvent = mapAIStreamDTOToEvent(rawData as AIStreamDTO);
      handleAIStream(domainEvent as AIStreamEvent);
      break;
    case 'subscription.updated':
      domainEvent = mapSubscriptionUpdatedDTOToEvent(rawData as SubscriptionUpdatedDTO);
      handleSubscriptionUpdated(domainEvent as SubscriptionUpdatedEvent, queryClient);
      break;
    case 'profile.updated':
      domainEvent = mapProfileUpdatedDTOToEvent(rawData as ProfileUpdatedDTO);
      handleProfileUpdated(domainEvent as ProfileUpdatedEvent, queryClient);
      break;
    default:
      // Unknown event type, do nothing
      return;
  }

  if (broadcastCallback && domainEvent) {
    broadcastCallback(type, domainEvent);
  }
};
