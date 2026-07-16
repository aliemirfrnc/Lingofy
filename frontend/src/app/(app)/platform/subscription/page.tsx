import { AuthenticatedOnly } from '@/providers/AuthProvider';
import { 
  CurrentPlanCard, 
  UsageCard, 
  BillingOverviewCard, 
  InvoiceTable, 
  InvoiceHistoryCard,
  PlansCard 
} from '@/features/subscription';

export const metadata = {
  title: 'Subscription | Customer Platform',
};

export default function SubscriptionPage() {
  return (
    <AuthenticatedOnly>
      <div style={{ padding: 'var(--space-6)', maxWidth: '1000px', margin: '0 auto' }}>
        <h1 style={{ fontFamily: 'var(--font-family-base)', color: 'var(--color-text-primary)', marginBottom: 'var(--spacing-lg)' }}>Subscription Management</h1>
        
        <div style={{ display: 'grid', gap: 'var(--spacing-lg)', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
          <div>
            <CurrentPlanCard />
            <BillingOverviewCard />
            <UsageCard />
          </div>
          <div>
            <PlansCard />
            <InvoiceTable />
            <InvoiceHistoryCard />
          </div>
        </div>
      </div>
    </AuthenticatedOnly>
  );
}
