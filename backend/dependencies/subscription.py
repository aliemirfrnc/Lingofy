from fastapi import HTTPException, Request, Header
from functools import wraps

from backend.core.services.subscription_service import SubscriptionService
from backend.routes.auth import require_user_id

def enforce_usage_limit(feature: str, amount: int = 1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            authorization = kwargs.get('authorization')
            if request is None and authorization is None:
                raise HTTPException(status_code=500, detail="Middeware cannot find Request/Auth")
                
            user_id = require_user_id(request, authorization)
            can_use, msg = SubscriptionService.can_use_feature(user_id, feature, amount)
            
            if not can_use:
                raise HTTPException(status_code=403, detail={"error": "LIMIT_EXCEEDED", "message": msg, "feature": feature})
                
            result = await func(*args, **kwargs) if __import__('inspect').iscoroutinefunction(func) else func(*args, **kwargs)
            
            SubscriptionService.use_feature(user_id, feature, amount)
            return result
        return wrapper
    return decorator

def enforce_plan(min_level: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            authorization = kwargs.get('authorization')
            user_id = require_user_id(request, authorization)
            
            status = SubscriptionService.get_user_status(user_id)
            plan_name = status["plan"]["name"].upper()
            
            levels = {"FREE": 0, "PRO": 1, "MASTER": 2}
            
            if levels.get(plan_name, 0) < levels.get(min_level.upper(), 0):
                raise HTTPException(status_code=403, detail={"error": "UPGRADE_REQUIRED", "message": f"Bu özellik için en az {min_level} planı gerekiyor."})
            
            return await func(*args, **kwargs) if __import__('inspect').iscoroutinefunction(func) else func(*args, **kwargs)
        return wrapper
    return decorator
