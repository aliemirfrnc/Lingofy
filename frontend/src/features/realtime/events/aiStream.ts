import { AIStreamEvent } from '../models/realtimeModels';

export const handleAIStream = (
  event: AIStreamEvent
) => {
  // ai.stream -> stream state update
  // The actual state update will happen in the context or custom hook that subscribes to this.
};
