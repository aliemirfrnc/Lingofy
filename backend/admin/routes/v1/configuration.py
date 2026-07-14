from fastapi import APIRouter, Depends
from backend.admin.security.authorization import requires_permission

router = APIRouter()

@router.get("")
def get_configurations(admin: dict = Depends(requires_permission("system.view"))):
    # Mock return for configs
    return {
        "success": True,
        "data": [
            {"key": "AI_RATE_LIMIT", "value_json": '{"limit": 100, "window": 3600}', "description": "Global AI requests limit"}
        ]
    }
