export class HeartbeatManager {
  private timeoutMs: number;
  private timerId: ReturnType<typeof setTimeout> | null = null;
  private onTimeout: () => void;

  constructor(timeoutMs: number, onTimeout: () => void) {
    this.timeoutMs = timeoutMs;
    this.onTimeout = onTimeout;
  }

  public ping() {
    this.clear();
    this.timerId = setTimeout(() => {
      this.onTimeout();
    }, this.timeoutMs);
  }

  public clear() {
    if (this.timerId) {
      clearTimeout(this.timerId);
      this.timerId = null;
    }
  }
}
