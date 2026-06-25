from typing import Dict, Any
import uuid
import time
from backend.core.providers.payment_provider import PaymentProvider

class MockPaymentProvider(PaymentProvider):
    """
    Test ortamı için sahte ödeme sağlayıcısı.
    """
    def create_subscription(self, user_id: int, plan_id: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "provider_subscription_id": f"mock_sub_{uuid.uuid4().hex[:8]}",
            "provider_customer_id": f"mock_cus_{user_id}",
            "expires_at": time.time() + (30 * 24 * 60 * 60) # 30 days
        }

    def cancel_subscription(self, subscription_id: str) -> bool:
        return True
        
    def verify_payment(self, transaction_id: str) -> bool:
        return True
