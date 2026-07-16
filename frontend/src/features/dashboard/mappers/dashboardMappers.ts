import { ProgressStatsDTO } from '../services/dashboardService';
import { ProgressStats } from '../models/dashboardModels';

export const mapProgressStatsToDomain = (dto: ProgressStatsDTO): ProgressStats => {
  return {
    dailyScore: dto.daily_score,
    totalTimeMinutes: dto.total_time_minutes,
    completedSongs: dto.completed_songs,
    currentLevel: dto.current_level,
    cefrLevel: dto.cefr_level,
    totalXp: dto.total_xp,
    history: dto.history.map(h => ({
      date: h.date,
      score: h.score,
    })),
    badges: dto.badges.map(b => ({
      id: b.id,
      icon: b.icon,
      name: b.name,
      isUnlocked: b.unlocked, // Normalizing boolean property
    })),
    worstWords: dto.worst_words.map(w => ({
      word: w.word,
      correctCount: w.correct,
      wrongCount: w.wrong,
      errorRate: w.error_rate,
    })),
    dailyGoal: dto.daily_goal,
    phonemeProgress: dto.phoneme_progress.map(p => ({
      sound: p.sound,
      startScore: p.start,
      currentScore: p.current,
      improvement: p.improvement,
    })),
    motivation: dto.motivation,
  };
};
