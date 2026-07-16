export interface SubscriptionPlanDTO {
  name: string;
  price: number;
  currency: string;
  limits: {
    songs: number;
    words: number;
    ai_messages: number;
    shadowing_minutes: number;
    pronunciation: number;
  };
  features: {
    pdf_report: boolean;
    ai_mentor: boolean;
    speaking_simulation: boolean;
  };
}

export interface MyPlanDTO {
  plan: {
    id: number;
    name: string;
    price: number;
    currency: string;
    songs_limit: number;
    words_limit: number;
    ai_messages_limit: number;
    shadowing_limit: number;
    pronunciation_limit: number;
  };
  subscription: {
    id: number;
    status: string;
    started_at: string;
    expires_at: string;
    provider: string;
    cancel_at_period_end: boolean;
  } | null;
  usage: Record<string, number>;
}

export interface UsageFeatureDTO {
  today: number;
  current_period: number;
  plan_limit: number;
  remaining: number | null;
  reset_at: string;
}

export interface SubscriptionUsageDTO {
  songs: UsageFeatureDTO;
  words: UsageFeatureDTO;
  ai_messages: UsageFeatureDTO;
  pronunciation: UsageFeatureDTO;
  shadowing_minutes: UsageFeatureDTO;
}

export interface BillingOverviewDTO {
  plan: {
    name: string;
    price: number;
    currency: string;
  };
  subscription: {
    status: string;
    started_at: string;
    expires_at: string;
    provider: string;
    cancel_at_period_end: boolean;
  } | null;
  last_payment: {
    amount: number;
    currency: string;
    status: string;
    paid_at: string;
  } | null;
}

export interface InvoiceDTO {
  id: number;
  provider: string;
  amount: number;
  currency: string;
  status: string;
  invoice_id: string;
  transaction_id: string;
  created_at: string;
}

export interface InvoiceHistoryDTO {
  id: number;
  plan_name: string;
  status: string;
  provider: string;
  started_at: string;
  expires_at: string;
  cancel_at_period_end: boolean;
  created_at: string;
}

export interface PaymentMethodDTO {
  id: string;
  type: string;
  label: string;
}

export interface UpgradePlanResponseDTO {
  status: string;
  message: string;
}
