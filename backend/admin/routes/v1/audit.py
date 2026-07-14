from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.admin.security.authorization import requires_permission
from backend.admin.repositories.audit_read_repo import AuditReadRepository

router = APIRouter()
audit_repo = AuditReadRepository()

@router.get("")
def list_audit_logs(
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    action: Optional[str] = Query(None),
    admin: dict = Depends(requires_permission("system.view"))
):
    logs = audit_repo.get_audit_logs_paginated(cursor, limit, action)
    next_cursor = logs[-1]["id"] if logs else None
    return {
        "success": True,
        "data": logs,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": len(logs) == limit
        }
    }
