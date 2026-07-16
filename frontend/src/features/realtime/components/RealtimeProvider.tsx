'use client';

import { ReactNode, useEffect, useState, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { RealtimeContext } from '../context/RealtimeContext';
import { RealtimeService } from '../services/realtimeService';
import { ConnectionState, RealtimeEventCallback } from '../models/realtimeModels';
import { useAuth } from '@/providers/AuthProvider';

interface RealtimeProviderProps {
  children: ReactNode;
}

// In Next.js, we usually want to connect to an absolute or relative path that points to the API.
// Since apiClient uses process.env.NEXT_PUBLIC_API_URL, we should try to reuse the same logic.
const SSE_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/events/stream` 
  : '/api/events/stream';

export function RealtimeProvider({ children }: RealtimeProviderProps) {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuth();
  const [connectionState, setConnectionState] = useState<ConnectionState>('offline');

  const realtimeService = useMemo(() => {
    return new RealtimeService(SSE_URL, queryClient);
  }, [queryClient]);

  useEffect(() => {
    realtimeService.setOnStateChange(setConnectionState);

    if (isAuthenticated) {
      realtimeService.connect();
    } else {
      realtimeService.disconnect();
    }

    return () => {
      realtimeService.disconnect();
    };
  }, [realtimeService, isAuthenticated]);

  const value = useMemo(() => ({
    connectionState,
    subscribe: (callback: RealtimeEventCallback) => realtimeService.subscribe(callback),
  }), [connectionState, realtimeService]);

  return (
    <RealtimeContext.Provider value={value}>
      {/* 
        Accessibility requirement: Connection status readable by screen readers.
        We place a visually hidden element for screen readers.
      */}
      <div 
        role="status" 
        aria-live="polite" 
        style={{ 
          position: 'absolute', 
          width: '1px', 
          height: '1px', 
          padding: 0, 
          margin: '-1px', 
          overflow: 'hidden', 
          clip: 'rect(0, 0, 0, 0)', 
          whiteSpace: 'nowrap', 
          border: 0 
        }}
      >
        Realtime connection is {connectionState}
      </div>
      {children}
    </RealtimeContext.Provider>
  );
}
