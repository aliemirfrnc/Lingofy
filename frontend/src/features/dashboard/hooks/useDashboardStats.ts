import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import { dashboardService } from '../services/dashboardService';
import { mapProgressStatsToDomain } from '../mappers/dashboardMappers';
import { ProgressStats } from '../models/dashboardModels';

export function useDashboardStats() {
  return useQuery<ProgressStats, Error>({
    queryKey: queryKeys.dashboard(),
    queryFn: async () => {
      const response = await dashboardService.getStats();
      return mapProgressStatsToDomain(response);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
