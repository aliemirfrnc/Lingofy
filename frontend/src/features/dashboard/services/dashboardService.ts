import { apiClient } from '@/lib/app/api/client';

export interface BadgeDTO {
  id: number;
  icon: string;
  name: string;
  unlocked: boolean;
}

export interface WordStatDTO {
  word: string;
  correct: number;
  wrong: number;
  error_rate: number;
}

export interface HistoryDTO {
  date: string;
  score: number;
}

export interface PhonemeProgressDTO {
  sound: string;
  start: number;
  current: number;
  improvement: number;
}

export interface ProgressStatsDTO {
  daily_score: number;
  total_time_minutes: number;
  completed_songs: number;
  current_level: string;
  cefr_level: string;
  total_xp: number;
  history: HistoryDTO[];
  badges: BadgeDTO[];
  worst_words: WordStatDTO[];
  daily_goal: string;
  phoneme_progress: PhonemeProgressDTO[];
  motivation: string;
}

export const dashboardService = {
  getStats: async (): Promise<ProgressStatsDTO> => {
    const response = await apiClient.get<ProgressStatsDTO>('/api/progress/stats');
    return response.data;
  },
};
