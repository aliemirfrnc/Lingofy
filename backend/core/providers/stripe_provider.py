from typing import Dict, Any
from backend.core.providers.payment_provider import PaymentProvider

class StripeProvider(PaymentProvider):
    """
    Stripe Provider İskeleti.
    Gerçek entegrasyon için ileride doldurulacak.
    """
    def create_subscription(self, user_id: int, plan_id: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Stripe henüz yapılandırılmadı.")

    def cancel_subscription(self, subscription_id: str) -> bool:
        raise NotImplementedError("Stripe henüz yapılandırılmadı.")
        
    def verify_payment(self, transaction_id: str) -> bool:
        raise NotImplementedError("Stripe henüz yapılandırılmadı.")

    def verify_webhook(self, payload: bytes, signature: str | None) -> Dict[str, Any]:
        raise NotImplementedError("Stripe webhook doğrulaması yapılandırılmadı.")

    def refund(self, transaction_id: str, amount: float | None = None) -> Dict[str, Any]:
        raise NotImplementedError("Stripe refund yapılandırılmadı.")
