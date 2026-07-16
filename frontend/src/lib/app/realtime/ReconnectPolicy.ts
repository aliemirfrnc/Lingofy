/**
 * Calculates exponential backoff with jitter.
 * Sequence: 1, 2, 4, 8, 16, 30 max seconds.
 */
export const calculateBackoff = (retryCount: number, maxDelaySeconds: number = 30): number => {
  const baseDelay = Math.min(Math.pow(2, retryCount - 1), maxDelaySeconds);
  const jitter = baseDelay * (Math.random() * 0.2);
  return (baseDelay + jitter) * 1000;
};
