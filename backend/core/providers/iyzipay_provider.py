from typing import Dict, Any
from backend.core.providers.payment_provider import PaymentProvider

class IyzipayProvider(PaymentProvider):
    """
    İyzico Provider İskeleti.
    Gerçek entegrasyon için ileride doldurulacak.
    """
    def create_subscription(self, user_id: int, plan_id: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("İyzico henüz yapılandırılmadı.")

    def cancel_subscription(self, subscription_id: str) -> bool:
        raise NotImplementedError("İyzico henüz yapılandırılmadı.")
        
    def verify_payment(self, transaction_id: str) -> bool:
        raise NotImplementedError("İyzico henüz yapılandırılmadı.")
