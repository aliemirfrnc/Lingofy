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
        """
        Kullanıcının belirtilen özelliği kullanma limiti olup olmadığını kontrol eder.
        Döner: (İzin Verildi Mi, Hata Mesajı)
        """
        status = SubscriptionService.get_user_status(user_id)
        plan = status["plan"]
        usage = status["usage"]
        
        limit_key = f"{feature}_limit"
        used = usage.get(feature, 0)
        limit = plan.get(limit_key, 0)
        
        # 999999 is our 'unlimited' marker in DB
        if limit >= 999999:
            return True, ""
            
        if used + amount > limit:
            return False, f"Günlük limit doldu. ({used}/{limit}) Lingofy Pro veya Master'a yükseltin."
            
        return True, ""

    @staticmethod
    def use_feature(user_id: int, feature: str, amount: int = 1) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        repo.increment_usage(user_id, today, feature, amount)
