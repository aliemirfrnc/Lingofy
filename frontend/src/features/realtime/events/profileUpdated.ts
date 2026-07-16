import { QueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import { ProfileUpdatedEvent } from '../models/realtimeModels';

export const handleProfileUpdated = (
  event: ProfileUpdatedEvent,
  queryClient: QueryClient
) => {
  if (event.updatedField === 'preferences') {
    queryClient.invalidateQueries({ queryKey: queryKeys.preferences() });
  } else if (event.updatedField === 'sessions') {
    queryClient.invalidateQueries({ queryKey: queryKeys.sessions() });
  } else {
    queryClient.invalidateQueries({ queryKey: queryKeys.profile() });
  }
};
