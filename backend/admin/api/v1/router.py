from fastapi import APIRouter
from backend.admin.api.v1.dashboard import router as dashboard_router
from backend.admin.api.v1.health import router as health_router
from backend.admin.api.v1.metrics import router as metrics_router
from backend.admin.api.v1.queue import router as queue_router
from backend.admin.api.v1.incident import router as incident_router
from backend.admin.api.v1.feature_flags import router as feature_flags_router
from backend.admin.api.v1.configuration import router as configuration_router
from backend.admin.api.v1.notifications import router as notifications_router
from backend.admin.api.v1.exports import router as exports_router
from backend.admin.api.v1.timeline import router as timeline_router
from backend.admin.api.v1.provider_status import router as provider_status_router

api_router = APIRouter()

api_router.include_router(dashboard_router)
api_router.include_router(health_router)
api_router.include_router(metrics_router)
api_router.include_router(queue_router)
api_router.include_router(incident_router)
api_router.include_router(feature_flags_router)
api_router.include_router(configuration_router)
api_router.include_router(notifications_router)
api_router.include_router(exports_router)
api_router.include_router(timeline_router)
api_router.include_router(provider_status_router)
