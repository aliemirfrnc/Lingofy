from fastapi import APIRouter
from backend.admin.routes.v1.users import router as users_router
from backend.admin.routes.v1.payments import router as payments_router
from backend.admin.routes.v1.system import router as system_router
from backend.admin.routes.v1.dashboard import router as dashboard_router
from backend.admin.routes.v1.audit import router as audit_router
from backend.admin.routes.v1.configuration import router as configuration_router

admin_v1_router = APIRouter()

admin_v1_router.include_router(users_router, prefix="/users", tags=["Admin Users"])
admin_v1_router.include_router(payments_router, prefix="/payments", tags=["Admin Payments"])
admin_v1_router.include_router(system_router, prefix="/system", tags=["Admin System"])
admin_v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["Admin Dashboard"])
admin_v1_router.include_router(audit_router, prefix="/audit", tags=["Admin Audit"])
admin_v1_router.include_router(configuration_router, prefix="/configuration", tags=["Admin Configuration"])
