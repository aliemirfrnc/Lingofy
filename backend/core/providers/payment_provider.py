from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentProviderUnavailable(RuntimeError):
    pass

class PaymentProvider(ABC):
    @abstractmethod
    def create_subscription(self, user_id: int, plan_id: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        pass
        
    @abstractmethod
    def verify_payment(self, transaction_id: str) -> bool:
        pass

    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str | None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def refund(self, transaction_id: str, amount: float | None = None) -> Dict[str, Any]:
        pass
