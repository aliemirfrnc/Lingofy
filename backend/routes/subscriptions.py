"""
/api/subscriptions — Subscription, usage, billing, invoices endpoints.

Architecture: Route → SubscriptionService → SubscriptionRepo → SQLite
No SQL in this file. No business logic in this file.

Endpoints:
  GET  /api/subscriptions/plans            → available plans (public, no auth)
  GET  /api/subscriptions/my-plan          → current user plan + today's usage
  GET  /api/subscriptions/usage            → detailed usage with limits and reset_at
  GET  /api/subscriptions/billing-overview → plan + payment history summary
  GET  /api/subscriptions/invoices         → payment history list
  GET  /api/subscriptions/invoices/{id}    → single invoice detail
  GET  /api/subscriptions/history          → subscription change history
  POST /api/subscriptions/upgrade          → upgrade plan (RFC7807 503 in production)

  POST /api/subscriptions/payment-methods  → RFC7807 503 (billing provider pending)
  GET  /api/subscriptions/payment-methods  → RFC7807 503 (billing provider pending)
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.core.db import get_conn, get_lock
from backend.core.services.subscription_service import SubscriptionService
from backend.routes.auth import require_user_id
from backend.core.providers.mock_provider import MockPaymentProvider
from backend.core.config import IS_PRODUCTION
from backend.core.logger import get_logger

logger = get_logger("lingofy.routes.subscriptions")

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# ---------------------------------------------------------------------------
# RFC7807 helper
# ---------------------------------------------------------------------------

def _billing_provider_unavailable() -> JSONResponse:
    """
    Documented RFC7807 503 response for endpoints requiring a billing provider.

    Clients must handle this gracefully (e.g., show 'Coming Soon' UI).
    The `Retry-After` header indicates when to check again.
    """
    return JSONResponse(
        status_code=503,
        headers={"Retry-After": "86400"},   # 24 hours
        content={
            "type": "https://lingofy.app/errors/billing-provider-unavailable",
            "title": "Billing Provider Unavailable",
            "status": 503,
            "detail": "The payment provider integration is not yet configured for this environment. "
                      "This feature will be available when billing is enabled.",
            "instance": "/api/subscriptions",
            "extensions": {
                "maintenance_code": "BILLING_PROVIDER_NOT_AVAILABLE",
                "provider": "PENDING",
                "retry_after": 86400,
            },
        },
    )


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------

class UpgradeRequest(BaseModel):
    plan_name: str
    payment_method_id: str = "mock_pm_123"


# ---------------------------------------------------------------------------
# GET /api/subscriptions/plans  (public — no auth required)
# ---------------------------------------------------------------------------

@router.get(
    "/plans",
    summary="Available subscription plans",
    response_description="List of all plans with limits and pricing.",
    tags=["subscriptions"],
)
def list_plans() -> List[Dict[str, Any]]:
    """Return all subscription plans. Does not require authentication."""
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            """
            SELECT name, price, currency,
                   songs_limit, words_limit, ai_messages_limit,
                   shadowing_limit, pronunciation_limit,
                   has_pdf_report, has_ai_mentor, has_speaking_sim
            FROM plans
            ORDER BY price ASC
            """
        )
        rows = cur.fetchall()
    return [
        {
            "name": r[0],
            "price": r[1],
            "currency": r[2] or "USD",
            "limits": {
                "songs": r[3],
                "words": r[4],
                "ai_messages": r[5],
                "shadowing_minutes": r[6],
                "pronunciation": r[7],
            },
            "features": {
                "pdf_report": bool(r[8]),
                "ai_mentor": bool(r[9]),
                "speaking_simulation": bool(r[10]),
            },
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/subscriptions/my-plan
# ---------------------------------------------------------------------------

@router.get(
    "/my-plan",
    summary="Current user plan",
    response_description="Active plan and today's usage.",
)
def get_my_plan(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Return the authenticated user's current plan and today's usage counters."""
    user_id = require_user_id(request, authorization)
    return SubscriptionService.get_user_status(user_id)


# ---------------------------------------------------------------------------
# GET /api/subscriptions/usage
# ---------------------------------------------------------------------------

@router.get(
    "/usage",
    summary="Detailed usage with limits",
    response_description=(
        "Today's usage per feature alongside plan limits, remaining count, and reset time."
    ),
)
def get_usage(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """
    Return granular usage data for the authenticated user.

    Response shape per feature:
    ```json
    {
      "today": 3,
      "current_period": 3,
      "plan_limit": 10,
      "remaining": 7,
      "reset_at": "2026-07-16T00:00:00Z"
    }
    ```
    """
    user_id = require_user_id(request, authorization)
    status = SubscriptionService.get_user_status(user_id)
    plan = status["plan"]
    usage = status["usage"]

    # Reset at midnight UTC
    now_utc = datetime.now(timezone.utc)
    reset_at = datetime(
        now_utc.year, now_utc.month, now_utc.day,
        tzinfo=timezone.utc,
    ).replace(day=now_utc.day + 1).isoformat()

    def feature_block(feature_key: str, limit_key: str) -> Dict[str, Any]:
        used: int = usage.get(feature_key, 0)
        limit: int = plan.get(limit_key, 0)
        return {
            "today": used,
            "current_period": used,
            "plan_limit": limit,
            "remaining": max(0, limit - used) if limit < 999999 else None,
            "reset_at": reset_at,
        }

    return {
        "songs": feature_block("songs", "songs_limit"),
        "words": feature_block("words", "words_limit"),
        "ai_messages": feature_block("ai_messages", "ai_messages_limit"),
        "pronunciation": feature_block("pronunciation", "pronunciation_limit"),
        "shadowing_minutes": feature_block("shadowing", "shadowing_limit"),
    }


# ---------------------------------------------------------------------------
# GET /api/subscriptions/billing-overview
# ---------------------------------------------------------------------------

@router.get(
    "/billing-overview",
    summary="Billing overview",
    response_description="Current plan details with last payment summary.",
)
def get_billing_overview(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Return a billing summary: current plan, subscription dates, and last payment."""
    user_id = require_user_id(request, authorization)
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            """
            SELECT s.status, s.started_at, s.expires_at, s.provider,
                   s.cancel_at_period_end, p.name, p.price, p.currency
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.id
            WHERE s.user_id = ? AND s.status = 'ACTIVE'
              AND s.expires_at > strftime('%s', 'now')
            ORDER BY s.expires_at DESC LIMIT 1
            """,
            (user_id,),
        )
        sub = cur.fetchone()

        cur2 = conn.execute(
            """
            SELECT amount, currency, status, created_at
            FROM payments
            WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (user_id,),
        )
        last_payment = cur2.fetchone()

    overview: Dict[str, Any] = {
        "plan": None,
        "subscription": None,
        "last_payment": None,
    }

    if sub:
        overview["plan"] = {
            "name": sub[5],
            "price": sub[6],
            "currency": sub[7] or "USD",
        }
        overview["subscription"] = {
            "status": sub[0],
            "started_at": datetime.utcfromtimestamp(sub[1]).isoformat() + "Z",
            "expires_at": datetime.utcfromtimestamp(sub[2]).isoformat() + "Z",
            "provider": sub[3],
            "cancel_at_period_end": bool(sub[4]),
        }
    else:
        overview["plan"] = {"name": "FREE", "price": 0, "currency": "USD"}

    if last_payment:
        overview["last_payment"] = {
            "amount": last_payment[0],
            "currency": last_payment[1] or "USD",
            "status": last_payment[2],
            "paid_at": datetime.utcfromtimestamp(last_payment[3]).isoformat() + "Z",
        }

    return overview


# ---------------------------------------------------------------------------
# GET /api/subscriptions/invoices
# ---------------------------------------------------------------------------

@router.get(
    "/invoices",
    summary="Payment invoice list",
    response_description="Chronological list of all payments.",
)
def list_invoices(
    request: Request,
    authorization: str | None = Header(default=None),
) -> List[Dict[str, Any]]:
    """Return the full payment history for the authenticated user."""
    user_id = require_user_id(request, authorization)
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            """
            SELECT id, provider, amount, currency, status, invoice_id, transaction_id, created_at
            FROM payments
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
    return [
        {
            "id": r[0],
            "provider": r[1],
            "amount": r[2],
            "currency": r[3] or "USD",
            "status": r[4],
            "invoice_id": r[5],
            "transaction_id": r[6],
            "created_at": datetime.utcfromtimestamp(r[7]).isoformat() + "Z",
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/subscriptions/invoices/{invoice_id}
# ---------------------------------------------------------------------------

@router.get(
    "/invoices/{invoice_id}",
    summary="Single invoice detail",
    response_description="Full details of a single payment record.",
)
def get_invoice(
    invoice_id: int,
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Return a single payment record belonging to the authenticated user."""
    user_id = require_user_id(request, authorization)
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            """
            SELECT id, provider, amount, currency, status, invoice_id, transaction_id, created_at
            FROM payments
            WHERE id = ? AND user_id = ?
            """,
            (invoice_id, user_id),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return {
        "id": row[0],
        "provider": row[1],
        "amount": row[2],
        "currency": row[3] or "USD",
        "status": row[4],
        "invoice_id": row[5],
        "transaction_id": row[6],
        "created_at": datetime.utcfromtimestamp(row[7]).isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# GET /api/subscriptions/history
# ---------------------------------------------------------------------------

@router.get(
    "/history",
    summary="Subscription change history",
    response_description="All historical subscriptions for the user.",
)
def get_subscription_history(
    request: Request,
    authorization: str | None = Header(default=None),
) -> List[Dict[str, Any]]:
    """Return all past and current subscription records for the authenticated user."""
    user_id = require_user_id(request, authorization)
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            """
            SELECT s.id, p.name, s.status, s.provider,
                   s.started_at, s.expires_at, s.cancel_at_period_end, s.created_at
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.id
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
    return [
        {
            "id": r[0],
            "plan_name": r[1],
            "status": r[2],
            "provider": r[3],
            "started_at": datetime.utcfromtimestamp(r[4]).isoformat() + "Z",
            "expires_at": datetime.utcfromtimestamp(r[5]).isoformat() + "Z",
            "cancel_at_period_end": bool(r[6]),
            "created_at": datetime.utcfromtimestamp(r[7]).isoformat() + "Z",
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# POST /api/subscriptions/upgrade  (BLOCKER-004: RFC7807 503 in production)
# ---------------------------------------------------------------------------

@router.post(
    "/upgrade",
    summary="Upgrade subscription plan",
    responses={
        200: {"description": "Upgrade successful (development/test only)."},
        400: {"description": "Invalid plan name."},
        503: {"description": "Billing provider not configured (production)."},
    },
)
def upgrade_plan(
    payload: UpgradeRequest,
    request: Request,
    authorization: str | None = Header(default=None),
):
    """
    Upgrade the user's subscription plan.

    **Production:** Returns RFC7807 503 until a billing provider is configured.
    This is a documented maintenance contract, not an error state.

    **Development/Test:** Uses the mock payment provider to complete the upgrade.
    """
    user_id = require_user_id(request, authorization)

    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            "SELECT id, price FROM plans WHERE name = ?",
            (payload.plan_name.upper(),),
        )
        plan = cur.fetchone()

    if not plan:
        raise HTTPException(status_code=400, detail="Geçersiz plan seçimi.")

    plan_id, price = plan

    if IS_PRODUCTION:
        return _billing_provider_unavailable()

    # Development/test only
    provider = MockPaymentProvider()
    result = provider.create_subscription(
        user_id, plan_id, {"pm_id": payload.payment_method_id}
    )
    if result.get("status") != "success":
        raise HTTPException(status_code=402, detail="Ödeme başarısız oldu.")

    now = time.time()
    with get_lock():
        conn.execute(
            "UPDATE subscriptions SET status = 'CANCELLED', updated_at = ? WHERE user_id = ? AND status = 'ACTIVE'",
            (now, user_id),
        )
        conn.execute(
            """
            INSERT INTO subscriptions
                (user_id, plan_id, status, provider, provider_subscription_id,
                 provider_customer_id, started_at, expires_at, created_at, updated_at)
            VALUES (?, ?, 'ACTIVE', 'MOCK', ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, plan_id,
                result["provider_subscription_id"],
                result["provider_customer_id"],
                now, result["expires_at"], now, now,
            ),
        )
        role = payload.plan_name.upper()
        if role in ("PRO", "MASTER"):
            conn.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (role, user_id),
            )
        conn.commit()

    logger.info(f"Subscription upgraded user_id={user_id} plan={payload.plan_name.upper()}")
    return {"status": "ok", "message": f"{payload.plan_name} planına başarıyla yükseltildi!"}


# ---------------------------------------------------------------------------
# Payment Methods — RFC7807 503 until billing provider is integrated
# ---------------------------------------------------------------------------

@router.get(
    "/payment-methods",
    summary="List payment methods",
    responses={503: {"description": "Billing provider not configured."}},
)
def list_payment_methods(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """
    List saved payment methods.

    **Status:** Billing provider integration pending.
    Returns RFC7807 503 until a real payment provider is configured.
    """
    require_user_id(request, authorization)
    return _billing_provider_unavailable()


@router.post(
    "/payment-methods",
    summary="Add payment method",
    responses={503: {"description": "Billing provider not configured."}},
)
def add_payment_method(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """
    Add a new payment method.

    **Status:** Billing provider integration pending.
    Returns RFC7807 503 until a real payment provider is configured.
    """
    require_user_id(request, authorization)
    return _billing_provider_unavailable()
