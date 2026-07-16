import {
  SubscriptionPlanDTO,
  SubscriptionUsageDTO,
  UsageFeatureDTO,
  BillingOverviewDTO,
  InvoiceDTO,
  InvoiceHistoryDTO,
  MyPlanDTO,
} from '../types';
import {
  SubscriptionPlan,
  SubscriptionUsage,
  FeatureLimit,
  BillingOverview,
  Invoice,
  InvoiceHistory,
  CurrentPlan,
} from '../models/SubscriptionModels';

export const mapFeatureLimitDTOToDomain = (dto: UsageFeatureDTO): FeatureLimit => ({
  today: dto.today,
  currentPeriod: dto.current_period,
  planLimit: dto.plan_limit,
  remaining: dto.remaining,
  resetAt: new Date(dto.reset_at),
});

export const mapUsageDTOToDomain = (dto: SubscriptionUsageDTO): SubscriptionUsage => ({
  songs: mapFeatureLimitDTOToDomain(dto.songs),
  words: mapFeatureLimitDTOToDomain(dto.words),
  aiMessages: mapFeatureLimitDTOToDomain(dto.ai_messages),
  pronunciation: mapFeatureLimitDTOToDomain(dto.pronunciation),
  shadowingMinutes: mapFeatureLimitDTOToDomain(dto.shadowing_minutes),
});

export const mapPlanDTOToDomain = (dto: SubscriptionPlanDTO): SubscriptionPlan => ({
  name: dto.name,
  price: dto.price,
  currency: dto.currency,
  limits: {
    songs: dto.limits.songs,
    words: dto.limits.words,
    aiMessages: dto.limits.ai_messages,
    shadowingMinutes: dto.limits.shadowing_minutes,
    pronunciation: dto.limits.pronunciation,
  },
  features: {
    pdfReport: dto.features.pdf_report,
    aiMentor: dto.features.ai_mentor,
    speakingSimulation: dto.features.speaking_simulation,
  },
});

export const mapMyPlanDTOToDomain = (dto: MyPlanDTO): CurrentPlan => ({
  planName: dto.plan.name,
  price: dto.plan.price,
  currency: dto.plan.currency,
  status: dto.subscription ? dto.subscription.status : null,
  startedAt: dto.subscription ? new Date(dto.subscription.started_at) : null,
  expiresAt: dto.subscription ? new Date(dto.subscription.expires_at) : null,
  provider: dto.subscription ? dto.subscription.provider : null,
  cancelAtPeriodEnd: dto.subscription ? dto.subscription.cancel_at_period_end : false,
});

export const mapBillingOverviewDTOToDomain = (dto: BillingOverviewDTO): BillingOverview => ({
  planName: dto.plan.name,
  price: dto.plan.price,
  currency: dto.plan.currency,
  status: dto.subscription ? dto.subscription.status : null,
  startedAt: dto.subscription ? new Date(dto.subscription.started_at) : null,
  expiresAt: dto.subscription ? new Date(dto.subscription.expires_at) : null,
  provider: dto.subscription ? dto.subscription.provider : null,
  cancelAtPeriodEnd: dto.subscription ? dto.subscription.cancel_at_period_end : false,
  lastPayment: dto.last_payment ? {
    amount: dto.last_payment.amount,
    currency: dto.last_payment.currency,
    status: dto.last_payment.status,
    paidAt: new Date(dto.last_payment.paid_at),
  } : null,
});

export const mapInvoiceDTOToDomain = (dto: InvoiceDTO): Invoice => ({
  id: dto.id,
  provider: dto.provider,
  amount: dto.amount,
  currency: dto.currency,
  status: dto.status,
  invoiceId: dto.invoice_id,
  transactionId: dto.transaction_id,
  createdAt: new Date(dto.created_at),
});

export const mapInvoiceHistoryDTOToDomain = (dto: InvoiceHistoryDTO): InvoiceHistory => ({
  id: dto.id,
  planName: dto.plan_name,
  status: dto.status,
  provider: dto.provider,
  startedAt: new Date(dto.started_at),
  expiresAt: new Date(dto.expires_at),
  cancelAtPeriodEnd: dto.cancel_at_period_end,
  createdAt: new Date(dto.created_at),
});
