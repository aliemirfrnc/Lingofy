export type SubscriptionErrorType =
  | 'Validation'
  | 'Unauthorized'
  | 'Forbidden'
  | 'Maintenance'
  | 'Offline'
  | 'Unknown';

export class SubscriptionError extends Error {
  public type: SubscriptionErrorType;
  public fieldErrors?: Record<string, string[]>;
  public status?: number;
  public retryAfter?: number;

  constructor(
    message: string,
    type: SubscriptionErrorType = 'Unknown',
    fieldErrors?: Record<string, string[]>,
    status?: number,
    retryAfter?: number
  ) {
    super(message);
    this.name = 'SubscriptionError';
    this.type = type;
    this.fieldErrors = fieldErrors;
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

export interface FeatureLimit {
  today: number;
  currentPeriod: number;
  planLimit: number;
  remaining: number | null;
  resetAt: Date;
}

export interface SubscriptionUsage {
  songs: FeatureLimit;
  words: FeatureLimit;
  aiMessages: FeatureLimit;
  pronunciation: FeatureLimit;
  shadowingMinutes: FeatureLimit;
}

export interface SubscriptionPlan {
  name: string;
  price: number;
  currency: string;
  limits: {
    songs: number;
    words: number;
    aiMessages: number;
    shadowingMinutes: number;
    pronunciation: number;
  };
  features: {
    pdfReport: boolean;
    aiMentor: boolean;
    speakingSimulation: boolean;
  };
}

export interface CurrentPlan {
  planName: string;
  price: number;
  currency: string;
  status: string | null;
  startedAt: Date | null;
  expiresAt: Date | null;
  provider: string | null;
  cancelAtPeriodEnd: boolean;
}

export interface BillingOverview {
  planName: string;
  price: number;
  currency: string;
  status: string | null;
  startedAt: Date | null;
  expiresAt: Date | null;
  provider: string | null;
  cancelAtPeriodEnd: boolean;
  lastPayment: {
    amount: number;
    currency: string;
    status: string;
    paidAt: Date;
  } | null;
}

export interface Invoice {
  id: number;
  provider: string;
  amount: number;
  currency: string;
  status: string;
  invoiceId: string;
  transactionId: string;
  createdAt: Date;
}

export interface InvoiceHistory {
  id: number;
  planName: string;
  status: string;
  provider: string;
  startedAt: Date;
  expiresAt: Date;
  cancelAtPeriodEnd: boolean;
  createdAt: Date;
}
