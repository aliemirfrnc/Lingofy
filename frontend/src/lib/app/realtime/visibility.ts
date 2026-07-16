export class VisibilityManager {
  private onVisible: () => void;
  private onHidden: () => void;
  private onOnline: () => void;
  private onOffline: () => void;

  constructor(
    onVisible: () => void,
    onHidden: () => void,
    onOnline: () => void,
    onOffline: () => void
  ) {
    this.onVisible = onVisible;
    this.onHidden = onHidden;
    this.onOnline = onOnline;
    this.onOffline = onOffline;

    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
    this.handleOnline = this.handleOnline.bind(this);
    this.handleOffline = this.handleOffline.bind(this);
  }

  public get isVisible(): boolean {
    return typeof document !== 'undefined' ? document.visibilityState === 'visible' : true;
  }

  public get isOnline(): boolean {
    return typeof navigator !== 'undefined' ? navigator.onLine : true;
  }

  public setup() {
    if (typeof window !== 'undefined') {
      document.addEventListener('visibilitychange', this.handleVisibilityChange);
      window.addEventListener('online', this.handleOnline);
      window.addEventListener('offline', this.handleOffline);
      window.addEventListener('focus', this.handleVisibilityChange);
      window.addEventListener('blur', this.handleVisibilityChange);
    }
  }

  public cleanup() {
    if (typeof window !== 'undefined') {
      document.removeEventListener('visibilitychange', this.handleVisibilityChange);
      window.removeEventListener('online', this.handleOnline);
      window.removeEventListener('offline', this.handleOffline);
      window.removeEventListener('focus', this.handleVisibilityChange);
      window.removeEventListener('blur', this.handleVisibilityChange);
    }
  }

  private handleVisibilityChange() {
    if (this.isVisible) {
      this.onVisible();
    } else {
      this.onHidden();
    }
  }

  private handleOnline() {
    this.onOnline();
  }

  private handleOffline() {
    this.onOffline();
  }
}
