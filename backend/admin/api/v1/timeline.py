from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IAggregationQueryService

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get timeline",
    description="Returns timeline events with cursor pagination.",
    operation_id="get_timeline",
)
def get_timeline(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.TIMELINE_READ)),
    service: IAggregationQueryService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_timeline(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )
