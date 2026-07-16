import { apiClient } from '@/lib/app/api/client';
import {
  SubscriptionPlanDTO,
  SubscriptionUsageDTO,
  BillingOverviewDTO,
  InvoiceDTO,
  InvoiceHistoryDTO,
  MyPlanDTO,
  PaymentMethodDTO,
  UpgradePlanResponseDTO,
} from '../types';

export const getPlans = async (): Promise<SubscriptionPlanDTO[]> => {
  const { data } = await apiClient.get<SubscriptionPlanDTO[]>('/subscriptions/plans');
  return data;
};

export const getMyPlan = async (): Promise<MyPlanDTO> => {
  const { data } = await apiClient.get<MyPlanDTO>('/subscriptions/my-plan');
  return data;
};

export const getUsage = async (): Promise<SubscriptionUsageDTO> => {
  const { data } = await apiClient.get<SubscriptionUsageDTO>('/subscriptions/usage');
  return data;
};

export const getBillingOverview = async (): Promise<BillingOverviewDTO> => {
  const { data } = await apiClient.get<BillingOverviewDTO>('/subscriptions/billing-overview');
  return data;
};

export const getInvoices = async (): Promise<InvoiceDTO[]> => {
  const { data } = await apiClient.get<InvoiceDTO[]>('/subscriptions/invoices');
  return data;
};

export const getInvoice = async (invoiceId: number): Promise<InvoiceDTO> => {
  const { data } = await apiClient.get<InvoiceDTO>(`/subscriptions/invoices/${invoiceId}`);
  return data;
};

export const getHistory = async (): Promise<InvoiceHistoryDTO[]> => {
  const { data } = await apiClient.get<InvoiceHistoryDTO[]>('/subscriptions/history');
  return data;
};

export const getPaymentMethods = async (): Promise<PaymentMethodDTO[]> => {
  const { data } = await apiClient.get<PaymentMethodDTO[]>('/subscriptions/payment-methods');
  return data;
};

export const upgradePlan = async (planName: string, paymentMethodId: string): Promise<UpgradePlanResponseDTO> => {
  const { data } = await apiClient.post<UpgradePlanResponseDTO>('/subscriptions/upgrade', {
    plan_name: planName,
    payment_method_id: paymentMethodId,
  });
  return data;
};
