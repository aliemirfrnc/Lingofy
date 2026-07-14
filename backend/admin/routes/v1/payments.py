from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from backend.admin.security.authorization import requires_permission
from backend.admin.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()

@router.get("")
def list_payments(
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    admin: dict = Depends(requires_permission("payments.read"))
):
    payments = payment_service.get_payments(cursor, limit)
    next_cursor = payments[-1]["id"] if payments else None
    return {
        "success": True,
        "data": payments,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": len(payments) == limit
        }
    }

class RefundRequest(BaseModel):
    reason: str

@router.post("/{payment_id}/refund")
async def process_refund(
    payment_id: int,
    req: RefundRequest,
    request: Request,
    admin: dict = Depends(requires_permission("payments.refund"))
):
    ip_address = request.client.host if request.client else None
    try:
        await payment_service.process_refund(admin["id"], payment_id, req.reason, ip_address)
        return {"success": True, "message": "Refund processed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
