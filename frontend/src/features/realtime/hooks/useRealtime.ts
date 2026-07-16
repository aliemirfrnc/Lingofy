import { useContext, useEffect } from 'react';
import { RealtimeContext } from '../context/RealtimeContext';
import { RealtimeEventCallback } from '../models/realtimeModels';

export function useRealtime(onEvent?: RealtimeEventCallback) {
  const context = useContext(RealtimeContext);

  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }

  useEffect(() => {
    if (onEvent) {
      return context.subscribe(onEvent);
    }
  }, [context, onEvent]);

  return {
    connectionState: context.connectionState,
  };
}
