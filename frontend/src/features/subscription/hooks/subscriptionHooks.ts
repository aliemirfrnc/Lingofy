import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/app/queryKeys';
import {
  fetchPlans,
  fetchMyPlan,
  fetchUsage,
  fetchBillingOverview,
  fetchInvoices,
  fetchInvoice,
  fetchHistory,
  fetchPaymentMethods,
  executeUpgrade,
} from '../services/subscriptionApplicationService';
import {
  SubscriptionPlan,
  SubscriptionUsage,
  BillingOverview,
  Invoice,
  InvoiceHistory,
  CurrentPlan,
  SubscriptionError,
} from '../models/SubscriptionModels';
import { PaymentMethodDTO, UpgradePlanResponseDTO } from '../types';

export const usePlans = () => {
  return useQuery<SubscriptionPlan[], SubscriptionError>({
    queryKey: queryKeys.plans(),
    queryFn: fetchPlans,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
};

export const useSubscription = () => {
  return useQuery<CurrentPlan, SubscriptionError>({
    queryKey: queryKeys.subscription(),
    queryFn: fetchMyPlan,
  });
};

export const useUsage = () => {
  return useQuery<SubscriptionUsage, SubscriptionError>({
    queryKey: queryKeys.usage(),
    queryFn: fetchUsage,
    refetchInterval: 1000 * 60 * 5, // auto-refresh every 5 mins
  });
};

export const useBillingOverview = () => {
  return useQuery<BillingOverview, SubscriptionError>({
    queryKey: queryKeys.billingOverview(),
    queryFn: fetchBillingOverview,
  });
};

export const useInvoices = () => {
  return useQuery<Invoice[], SubscriptionError>({
    queryKey: queryKeys.invoices(),
    queryFn: fetchInvoices,
  });
};

export const useInvoice = (invoiceId: number) => {
  return useQuery<Invoice, SubscriptionError>({
    queryKey: queryKeys.invoice(invoiceId),
    queryFn: () => fetchInvoice(invoiceId),
    enabled: !!invoiceId,
  });
};

export const useHistory = () => {
  return useQuery<InvoiceHistory[], SubscriptionError>({
    queryKey: queryKeys.history(),
    queryFn: fetchHistory,
  });
};

export const usePaymentMethods = () => {
  return useQuery<PaymentMethodDTO[], SubscriptionError>({
    queryKey: queryKeys.paymentMethods(),
    queryFn: fetchPaymentMethods,
    retry: false, // Don't retry if 503 Maintenance
  });
};

export const useUpgrade = () => {
  const queryClient = useQueryClient();

  return useMutation<UpgradePlanResponseDTO, SubscriptionError, { planName: string, paymentMethodId: string }>({
    mutationFn: ({ planName, paymentMethodId }) => executeUpgrade(planName, paymentMethodId),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.subscription() });
      queryClient.invalidateQueries({ queryKey: queryKeys.billingOverview() });
    }
  });
};
