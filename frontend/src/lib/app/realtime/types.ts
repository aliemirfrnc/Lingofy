export type ConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'offline' | 'error';

export interface SSEClientOptions {
  url: string;
  onStateChange?: (state: ConnectionState) => void;
  onMessage?: (event: MessageEvent) => void;
  onError?: (error: Error) => void;
  eventTypes?: readonly string[];
  maxRetries?: number;
}
