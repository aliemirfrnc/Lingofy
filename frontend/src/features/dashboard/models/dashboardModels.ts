export interface Badge {
  id: number;
  icon: string;
  name: string;
  isUnlocked: boolean;
}

export interface WordStat {
  word: string;
  correctCount: number;
  wrongCount: number;
  errorRate: number;
}

export interface HistoryRecord {
  date: string;
  score: number;
}

export interface PhonemeProgress {
  sound: string;
  startScore: number;
  currentScore: number;
  improvement: number;
}

export interface ProgressStats {
  dailyScore: number;
  totalTimeMinutes: number;
  completedSongs: number;
  currentLevel: string;
  cefrLevel: string;
  totalXp: number;
  history: HistoryRecord[];
  badges: Badge[];
  worstWords: WordStat[];
  dailyGoal: string;
  phonemeProgress: PhonemeProgress[];
  motivation: string;
}
