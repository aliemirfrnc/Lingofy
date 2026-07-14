import time
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Dict, Any

from backend.core.db import get_conn, get_lock
from backend.routes.auth import require_user_id
from backend.core.providers.mock_provider import MockPaymentProvider
from backend.core.config import IS_PRODUCTION

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

class UpgradeRequest(BaseModel):
    plan_name: str
    payment_method_id: str = "mock_pm_123"

@router.post("/upgrade")
def upgrade_plan(payload: UpgradeRequest, request: Request, authorization: str | None = Header(default=None)):
    user_id = require_user_id(request, authorization)
    
    # Check if plan exists
    conn = get_conn()
    with get_lock():
        cur = conn.execute("SELECT id, price FROM plans WHERE name = ?", (payload.plan_name.upper(),))
        plan = cur.fetchone()
        
    if not plan:
        raise HTTPException(status_code=400, detail="Geçersiz plan seçimi.")
        
    plan_id, price = plan
    
    if IS_PRODUCTION:
        # A production provider is intentionally required before money-changing actions.
        raise HTTPException(status_code=503, detail="Ödeme sağlayıcısı henüz yapılandırılmadı.")

    # Development/test only provider; production is explicitly denied above.
    provider = MockPaymentProvider()
    result = provider.create_subscription(user_id, plan_id, {"pm_id": payload.payment_method_id})
    
    if result.get("status") != "success":
        raise HTTPException(status_code=402, detail="Ödeme başarısız oldu.")
        
    # Cancel existing active subscriptions
    now = time.time()
    with get_lock():
        conn.execute("UPDATE subscriptions SET status = 'CANCELLED', updated_at = ? WHERE user_id = ? AND status = 'ACTIVE'", (now, user_id))
        
        # Insert new subscription
        conn.execute("""
            INSERT INTO subscriptions (user_id, plan_id, status, provider, provider_subscription_id, provider_customer_id, started_at, expires_at, created_at, updated_at)
            VALUES (?, ?, 'ACTIVE', 'MOCK', ?, ?, ?, ?, ?, ?)
        """, (user_id, plan_id, result["provider_subscription_id"], result["provider_customer_id"], now, result["expires_at"], now, now))
        
        # Update user role if PRO or MASTER
        role = payload.plan_name.upper()
        if role in ["PRO", "MASTER"]:
            conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
            
        conn.commit()
        
    return {"status": "ok", "message": f"{payload.plan_name} planına başarıyla yükseltildi!"}

@router.get("/my-plan")
def get_my_plan(request: Request, authorization: str | None = Header(default=None)):
    user_id = require_user_id(request, authorization)
    from backend.core.services.subscription_service import SubscriptionService
    return SubscriptionService.get_user_status(user_id)
