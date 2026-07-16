from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IMetricsQueryService

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get(
    "",
    response_model=SuccessResponse[dict],
    summary="Get metrics",
    description="Returns aggregated metrics data.",
    operation_id="get_metrics",
)
def get_metrics(
    admin: dict = Depends(requires_permission(Permission.METRICS_READ)),
    service: IMetricsQueryService = Depends()
) -> SuccessResponse[dict]:
    # Phase 5: No business logic
    data = service.get_metrics()
    return SuccessResponse(data=data)

@router.get(
    "/history",
    response_model=CursorResponse[dict],
    summary="Get metrics history",
    description="Returns metrics history with cursor pagination.",
    operation_id="get_metrics_history",
)
def get_metrics_history(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.METRICS_READ)),
    service: IMetricsQueryService = Depends()
) -> CursorResponse[dict]:
    # Using dictionary format for cursor response
    data, next_cursor, prev_cursor, total = service.get_metrics_history(filters.model_dump())
    return CursorResponse(
        data=data,
        cursor=filters.cursor,
        next_cursor=next_cursor,
        previous_cursor=prev_cursor,
        limit=filters.limit,
        total_count=total
    )

@router.get(
    "/providers",
    response_model=SuccessResponse[dict],
    summary="Get providers metrics",
    description="Returns metrics per provider.",
    operation_id="get_metrics_providers",
)
def get_metrics_providers(
    admin: dict = Depends(requires_permission(Permission.METRICS_READ)),
    service: IMetricsQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.get_providers_metrics()
    return SuccessResponse(data=data)
