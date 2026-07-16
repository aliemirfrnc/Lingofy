import { QueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import { SubscriptionUpdatedEvent } from '../models/realtimeModels';

export const handleSubscriptionUpdated = (
  event: SubscriptionUpdatedEvent,
  queryClient: QueryClient
) => {
  if (event.updatedField === 'plan') {
    queryClient.invalidateQueries({ queryKey: queryKeys.subscription() });
    queryClient.invalidateQueries({ queryKey: queryKeys.plans() });
  } else if (event.updatedField === 'usage') {
    queryClient.invalidateQueries({ queryKey: queryKeys.usage() });
  } else if (event.updatedField === 'billing') {
    queryClient.invalidateQueries({ queryKey: queryKeys.billingOverview() });
  } else {
    queryClient.invalidateQueries({ queryKey: queryKeys.subscription() });
  }
};
