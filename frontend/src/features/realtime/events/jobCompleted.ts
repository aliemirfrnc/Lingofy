import { QueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import { JobCompletedEvent } from '../models/realtimeModels';

export const handleJobCompleted = (
  event: JobCompletedEvent,
  queryClient: QueryClient
) => {
  // job.completed -> invalidate dashboard
  queryClient.invalidateQueries({ queryKey: queryKeys.dashboard() });
};
