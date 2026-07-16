import { JobProgressEvent } from '../models/realtimeModels';

export const handleJobProgress = (
  event: JobProgressEvent
) => {
  // job.progress updates will be handled by components listening to the event bus / context.
  // We can just log or broadcast it internally if needed.
};
