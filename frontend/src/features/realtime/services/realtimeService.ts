import { SSEClient, ConnectionError } from '@/lib/app/realtime';
import { ConnectionState, RealtimeEventCallback } from '../models/realtimeModels';
import { processRealtimeEvent } from '../events/eventRegistry';
import { QueryClient } from '@tanstack/react-query';

const REALTIME_EVENT_TYPES = [
  'notification',
  'job.progress',
  'job.completed',
  'job.failed',
  'ai.stream',
  'subscription.updated',
  'profile.updated',
] as const;

export class RealtimeService {
  private sseClient: SSEClient | null = null;
  private subscribers: Set<RealtimeEventCallback> = new Set();
  private queryClient: QueryClient;
  private url: string;
  private onStateChangeCb?: (state: ConnectionState) => void;

  constructor(url: string, queryClient: QueryClient) {
    this.url = url;
    this.queryClient = queryClient;
  }

  public setOnStateChange(cb: (state: ConnectionState) => void) {
    this.onStateChangeCb = cb;
  }

  public connect() {
    if (this.sseClient) return;

    this.sseClient = new SSEClient({
      url: this.url,
      maxRetries: 10,
      eventTypes: REALTIME_EVENT_TYPES,
      onStateChange: (state) => {
        if (this.onStateChangeCb) {
          this.onStateChangeCb(state);
        }
      },
      onMessage: (event) => {
        try {
          if (event.data === ': ping') return; // Ignore ping
          
          const type = event.type || 'message';
          if (type === 'message') {
            return;
          }

          const rawData = JSON.parse(event.data);
          
          processRealtimeEvent(
            type, 
            rawData, 
            this.queryClient,
            this.broadcast.bind(this)
          );

        } catch {
          // Malformed data is isolated to this event; keep the stream alive.
        }
      },
      onError: () => undefined,
    });

    this.sseClient.connect();
  }

  public disconnect() {
    if (this.sseClient) {
      this.sseClient.disconnect();
      this.sseClient = null;
    }
  }

  public subscribe(callback: RealtimeEventCallback): () => void {
    this.subscribers.add(callback);
    return () => {
      this.subscribers.delete(callback);
    };
  }

  private broadcast(type: string, payload: unknown) {
    this.subscribers.forEach(cb => cb(type, payload));
  }
}
