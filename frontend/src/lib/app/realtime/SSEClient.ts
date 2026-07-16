import { SSEClientOptions, ConnectionState } from './types';
import { calculateBackoff } from './ReconnectPolicy';
import { VisibilityManager } from './visibility';
import { HeartbeatManager } from './heartbeat';
import { ConnectionError } from './ConnectionError';

export class SSEClient {
  private url: string;
  private es: EventSource | null = null;
  private state: ConnectionState = 'offline';
  
  private retryCount = 0;
  private maxRetries: number;
  private retryTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private manualDisconnect = false;

  private visibility: VisibilityManager;
  private heartbeat: HeartbeatManager;

  private onStateChangeCb?: (state: ConnectionState) => void;
  private onMessageCb?: (event: MessageEvent) => void;
  private onErrorCb?: (error: ConnectionError) => void;
  private readonly eventTypes: readonly string[];

  constructor(options: SSEClientOptions) {
    this.url = options.url;
    this.onStateChangeCb = options.onStateChange;
    this.onMessageCb = options.onMessage;
    this.maxRetries = options.maxRetries ?? 10;
    this.eventTypes = options.eventTypes ?? [];
    this.onErrorCb = options.onError;

    this.visibility = new VisibilityManager(
      () => { if (!this.manualDisconnect) this.internalConnect(); }, // onVisible
      () => { this.cleanup(true); }, // onHidden
      () => { if (!this.manualDisconnect && this.visibility.isVisible) { this.retryCount = 0; this.internalConnect(); } }, // onOnline
      () => { this.cleanup(true); this.updateState('offline'); } // onOffline
    );

    // If no ping received for 60 seconds, assume connection is dead and reconnect
    this.heartbeat = new HeartbeatManager(60000, () => {
      this.handleError(new ConnectionError('Heartbeat timeout'));
    });
  }

  public connect() {
    this.manualDisconnect = false;
    this.visibility.setup();
    this.internalConnect();
  }

  public disconnect() {
    this.manualDisconnect = true;
    this.cleanup(false);
    this.visibility.cleanup();
    this.updateState('offline');
  }

  private internalConnect() {
    if (this.manualDisconnect || this.es || !this.visibility.isVisible || !this.visibility.isOnline) {
      return;
    }

    this.updateState(this.retryCount === 0 ? 'connecting' : 'reconnecting');

    try {
      this.es = new EventSource(this.url, { withCredentials: true });

      this.es.onopen = () => {
        this.retryCount = 0;
        this.updateState('connected');
        this.heartbeat.ping(); // start heartbeat on open
      };

      const handleMessage = (event: MessageEvent) => {
        if (event.data === ': ping') {
          this.heartbeat.ping();
          return;
        }
        this.heartbeat.ping();
        if (this.onMessageCb) {
          this.onMessageCb(event);
        }
      };
      this.es.onmessage = handleMessage;

      // EventSource only sends unnamed events to `onmessage`. Register each
      // named server event explicitly so the single connection is useful.
      for (const eventType of this.eventTypes) {
        this.es.addEventListener(eventType, handleMessage);
      }

      this.es.onerror = (error) => {
        this.handleError(new ConnectionError('SSE Connection Error'));
      };
    } catch (err) {
      this.handleError(new ConnectionError('Failed to create EventSource'));
    }
  }

  private handleError(error: ConnectionError) {
    this.cleanupEventSource();
    
    if (this.onErrorCb) {
      this.onErrorCb(error);
    }

    if (this.retryCount >= this.maxRetries) {
      this.updateState('error');
      return;
    }

    this.scheduleReconnect();
  }

  private scheduleReconnect() {
    if (this.retryTimeoutId) return;
    if (!this.visibility.isVisible || !this.visibility.isOnline) return;

    this.updateState('reconnecting');
    this.retryCount++;

    const delayMs = calculateBackoff(this.retryCount, 30);

    this.retryTimeoutId = setTimeout(() => {
      this.retryTimeoutId = null;
      this.internalConnect();
    }, delayMs);
  }

  private cleanupEventSource() {
    if (this.es) {
      this.es.close();
      this.es = null;
    }
  }

  private cleanup(keepRetryCount: boolean) {
    this.cleanupEventSource();
    this.heartbeat.clear();
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
      this.retryTimeoutId = null;
    }
    if (!keepRetryCount) {
      this.retryCount = 0;
    }
  }

  private updateState(newState: ConnectionState) {
    if (this.state !== newState) {
      this.state = newState;
      if (this.onStateChangeCb) {
        this.onStateChangeCb(newState);
      }
    }
  }
}
