import {
  getPlans,
  getMyPlan,
  getUsage,
  getBillingOverview,
  getInvoices,
  getInvoice,
  getHistory,
  getPaymentMethods,
  upgradePlan,
} from './subscriptionApiService';
import {
  mapPlanDTOToDomain,
  mapMyPlanDTOToDomain,
  mapUsageDTOToDomain,
  mapBillingOverviewDTOToDomain,
  mapInvoiceDTOToDomain,
  mapInvoiceHistoryDTOToDomain,
} from '../mappers/SubscriptionMappers';
import {
  SubscriptionPlan,
  SubscriptionUsage,
  BillingOverview,
  Invoice,
  InvoiceHistory,
  CurrentPlan,
} from '../models/SubscriptionModels';
import { SubscriptionError, SubscriptionErrorType } from '../models/SubscriptionModels';
import { PaymentMethodDTO, UpgradePlanResponseDTO } from '../types';
import { ApiError } from '@/lib/app/api/client';

const handleApiError = (err: unknown): never => {
  if (err instanceof ApiError) {
    let type: SubscriptionErrorType = 'Unknown';
    if (err.status === 422 || err.status === 400) type = 'Validation';
    else if (err.status === 401) type = 'Unauthorized';
    else if (err.status === 403) type = 'Forbidden';
    else if (err.status === 503) type = 'Maintenance';
    else if (err.status === 0) type = 'Offline';

    const retryAfter = err.details?.extensions?.retry_after as number | undefined;

    throw new SubscriptionError(
      err.message,
      type,
      err.details?.errors,
      err.status,
      retryAfter
    );
  }
  throw new SubscriptionError('An unexpected error occurred', 'Unknown');
};

export const fetchPlans = async (): Promise<SubscriptionPlan[]> => {
  try {
    const dtos = await getPlans();
    return dtos.map(mapPlanDTOToDomain);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchMyPlan = async (): Promise<CurrentPlan> => {
  try {
    const dto = await getMyPlan();
    return mapMyPlanDTOToDomain(dto);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchUsage = async (): Promise<SubscriptionUsage> => {
  try {
    const dto = await getUsage();
    return mapUsageDTOToDomain(dto);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchBillingOverview = async (): Promise<BillingOverview> => {
  try {
    const dto = await getBillingOverview();
    return mapBillingOverviewDTOToDomain(dto);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchInvoices = async (): Promise<Invoice[]> => {
  try {
    const dtos = await getInvoices();
    return dtos.map(mapInvoiceDTOToDomain);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchInvoice = async (invoiceId: number): Promise<Invoice> => {
  try {
    const dto = await getInvoice(invoiceId);
    return mapInvoiceDTOToDomain(dto);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchHistory = async (): Promise<InvoiceHistory[]> => {
  try {
    const dtos = await getHistory();
    return dtos.map(mapInvoiceHistoryDTOToDomain);
  } catch (err) {
    return handleApiError(err);
  }
};

export const fetchPaymentMethods = async (): Promise<PaymentMethodDTO[]> => {
  try {
    return await getPaymentMethods();
  } catch (err) {
    return handleApiError(err);
  }
};

export const executeUpgrade = async (planName: string, paymentMethodId: string): Promise<UpgradePlanResponseDTO> => {
  try {
    return await upgradePlan(planName, paymentMethodId);
  } catch (err) {
    return handleApiError(err);
  }
};
