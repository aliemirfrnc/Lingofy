from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IRuntimeConfigurationQueryService
from backend.admin.api.dependencies.idempotency import verify_idempotency_key

router = APIRouter(prefix="/configuration", tags=["Configuration"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get configuration",
    description="Returns configuration items with cursor pagination.",
    operation_id="get_configuration",
)
def get_configuration(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.CONFIGURATION_READ)),
    service: IRuntimeConfigurationQueryService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_configuration(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )

@router.patch(
    "",
    response_model=SuccessResponse[dict],
    summary="Update configuration",
    description="Update a configuration item.",
    operation_id="update_configuration",
)
def update_configuration(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.CONFIGURATION_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IRuntimeConfigurationQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.update_configuration(payload)
    return SuccessResponse(data=data)

@router.post(
    "/rollback",
    response_model=SuccessResponse[dict],
    summary="Rollback configuration",
    description="Rollback configuration to a previous state.",
    operation_id="rollback_configuration",
)
def rollback_configuration(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.CONFIGURATION_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IRuntimeConfigurationQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.rollback_configuration(payload)
    return SuccessResponse(data=data)
