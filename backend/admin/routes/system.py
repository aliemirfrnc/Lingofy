from fastapi import APIRouter, Depends, Request
from backend.admin.dependencies import get_admin_id, audit_log

router = APIRouter()

@router.get("/ping")
def ping_admin(request: Request, admin_id: int = Depends(get_admin_id)):
    ip = request.client.host if request.client else "unknown"
    audit_log(admin_id, action="PING", resource="SYSTEM", ip_address=ip)
    return {"status": "ok", "message": "Admin operations console is alive", "admin_id": admin_id}
