from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IAggregationQueryService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get(
    "",
    response_model=SuccessResponse[dict],
    summary="Get dashboard overview",
    description="Returns aggregated metrics, KPI, queue stats and health for the admin dashboard.",
    operation_id="get_dashboard",
)
def get_dashboard(
    admin: dict = Depends(requires_permission(Permission.DASHBOARD_READ)),
    service: IAggregationQueryService = Depends()
) -> SuccessResponse[dict]:
    # Strictly Application Service Call
    data = service.get_dashboard_overview()
    return SuccessResponse(data=data)
