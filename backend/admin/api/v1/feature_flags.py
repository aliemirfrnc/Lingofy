from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IFeatureFlagQueryService
from backend.admin.api.dependencies.idempotency import verify_idempotency_key

router = APIRouter(prefix="/feature-flags", tags=["Feature Flags"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get feature flags",
    description="Returns a list of feature flags with cursor pagination.",
    operation_id="get_feature_flags",
)
def get_feature_flags(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.FEATURE_FLAG_READ)),
    service: IFeatureFlagQueryService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_feature_flags(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )

@router.post(
    "",
    response_model=SuccessResponse[dict],
    summary="Create feature flag",
    description="Create a new feature flag.",
    operation_id="create_feature_flag",
)
def create_feature_flag(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.FEATURE_FLAG_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IFeatureFlagQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.create_feature_flag(payload)
    return SuccessResponse(data=data)

@router.patch(
    "/{flag_id}",
    response_model=SuccessResponse[dict],
    summary="Update feature flag",
    description="Update an existing feature flag.",
    operation_id="update_feature_flag",
)
def update_feature_flag(
    flag_id: str,
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.FEATURE_FLAG_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IFeatureFlagQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.update_feature_flag(flag_id, payload)
    return SuccessResponse(data=data)

@router.post(
    "/{flag_id}/rollback",
    response_model=SuccessResponse[dict],
    summary="Rollback feature flag",
    description="Rollback a feature flag to its previous state.",
    operation_id="rollback_feature_flag",
)
def rollback_feature_flag(
    flag_id: str,
    admin: dict = Depends(requires_permission(Permission.FEATURE_FLAG_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IFeatureFlagQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.rollback_feature_flag(flag_id)
    return SuccessResponse(data=data)
