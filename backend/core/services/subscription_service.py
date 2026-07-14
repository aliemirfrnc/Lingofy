from datetime import datetime
from typing import Dict, Any, Tuple
from backend.core.repositories.subscription_repo import SubscriptionRepo

repo = SubscriptionRepo()

class SubscriptionService:
    @staticmethod
    def get_user_status(user_id: int) -> Dict[str, Any]:
        """Kullanıcının aktif plan bilgilerini ve güncel kullanımlarını döner."""
        plan = repo.get_user_plan(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        usage = repo.get_usage(user_id, today)
        return {
            "plan": plan,
            "usage": usage
        }

    @staticmethod
    def can_use_feature(user_id: int, feature: str, amount: int = 1) -> Tuple[bool, str]:
        # Geriye dönük uyumluluk için, sadece kontrol eder (artırmaz).
        status = SubscriptionService.get_user_status(user_id)
        plan = status["plan"]
        usage = status["usage"]
        
        limit_key = f"{feature}_limit"
        used = usage.get(feature, 0)
        limit = plan.get(limit_key, 0)
        
        if limit >= 999999:
            return True, ""
            
        if used + amount > limit:
            return False, f"Günlük limit doldu. ({used}/{limit}) Lingofy Pro veya Master'a yükseltin."
            
        return True, ""

    @staticmethod
    def use_feature(user_id: int, feature: str, amount: int = 1) -> None:
        # Eski kullanım (artırma)
        today = datetime.now().strftime("%Y-%m-%d")
        repo.increment_usage(user_id, today, feature, amount)

    @staticmethod
    def consume_feature_atomic(user_id: int, feature: str, amount: int = 1) -> Tuple[bool, str]:
        """
        Check ve Increment işlemini tek bir kilit (RLock) altında yapar.
        Race condition'ı engeller. Eğer limit varsa artırıp True döner.
        """
        from backend.core.db import get_lock
        with get_lock():
            can, msg = SubscriptionService.can_use_feature(user_id, feature, amount)
            if can:
                SubscriptionService.use_feature(user_id, feature, amount)
            return can, msg

