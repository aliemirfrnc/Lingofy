from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from backend.admin.security.authorization import requires_permission
from backend.admin.services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.get("")
def list_users(
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    search: Optional[str] = Query(None),
    admin: dict = Depends(requires_permission("users.read"))
):
    users = user_service.get_users(cursor, limit, search)
    next_cursor = users[-1]["id"] if users else None
    return {
        "success": True,
        "data": users,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": len(users) == limit
        }
    }

@router.get("/{user_id}")
def get_user_profile(
    user_id: int,
    admin: dict = Depends(requires_permission("users.read"))
):
    profile = user_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": profile}

class BanUserRequest(BaseModel):
    reason: str

@router.post("/{user_id}/ban")
async def ban_user(
    user_id: int,
    req: BanUserRequest,
    request: Request,
    admin: dict = Depends(requires_permission("users.ban"))
):
    ip_address = request.client.host if request.client else None
    await user_service.ban_user(admin["id"], user_id, req.reason, ip_address)
    return {"success": True, "message": "User banned successfully"}
