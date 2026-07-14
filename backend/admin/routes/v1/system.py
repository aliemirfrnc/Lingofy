from fastapi import APIRouter, Depends
from backend.admin.security.authorization import requires_permission
from backend.admin.services.system_service import SystemService

router = APIRouter()
system_service = SystemService()

@router.get("/health")
def get_system_health(admin: dict = Depends(requires_permission("system.view"))):
    metrics = system_service.get_health_metrics()
    return {"success": True, "data": metrics}

@router.get("/database")
def get_database_stats(admin: dict = Depends(requires_permission("system.view"))):
    stats = system_service.get_database_tables()
    return {"success": True, "data": stats}
