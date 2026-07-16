from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IHealthQueryService

router = APIRouter(prefix="/provider-status", tags=["Provider Status"])

@router.get(
    "",
    response_model=SuccessResponse[dict],
    summary="Get provider status",
    description="Returns the detailed status of all external providers.",
    operation_id="get_provider_status",
)
def get_provider_status(
    admin: dict = Depends(requires_permission(Permission.PROVIDER_STATUS_READ)),
    service: IHealthQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.get_provider_status()
    return SuccessResponse(data=data)
