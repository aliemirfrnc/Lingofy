from fastapi import APIRouter, Depends, Response
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IExportQueryService
from backend.admin.api.dependencies.idempotency import verify_idempotency_key

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get exports",
    description="Returns a list of exports with cursor pagination.",
    operation_id="get_exports",
)
def get_exports(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.EXPORT_READ)),
    service: IExportQueryService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_exports(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )

@router.post(
    "",
    response_model=SuccessResponse[dict],
    summary="Create export",
    description="Request a new data export.",
    operation_id="create_export",
)
def create_export(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.EXPORT_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IExportQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.create_export(payload)
    return SuccessResponse(data=data)

@router.get(
    "/{export_id}",
    summary="Download export",
    description="Download the generated export file (Streaming support).",
    operation_id="download_export",
)
def download_export(
    export_id: str,
    admin: dict = Depends(requires_permission(Permission.EXPORT_READ)),
    service: IExportQueryService = Depends()
):
    # This should return a StreamingResponse in a real scenario
    stream = service.download_export(export_id)
    return Response(content=stream, media_type="application/octet-stream")

@router.delete(
    "/{export_id}",
    response_model=SuccessResponse[dict],
    summary="Delete export",
    description="Delete an export file and record.",
    operation_id="delete_export",
)
def delete_export(
    export_id: str,
    admin: dict = Depends(requires_permission(Permission.EXPORT_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IExportQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.delete_export(export_id)
    return SuccessResponse(data=data)
