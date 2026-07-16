import { createContext } from 'react';
import { ConnectionState, RealtimeEventCallback } from '../models/realtimeModels';

export interface RealtimeContextValue {
  connectionState: ConnectionState;
  subscribe: (callback: RealtimeEventCallback) => () => void;
}

export const RealtimeContext = createContext<RealtimeContextValue>({
  connectionState: 'offline',
  subscribe: () => () => {},
});
