from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IQueueQueryService
from backend.admin.api.dependencies.idempotency import verify_idempotency_key

router = APIRouter(prefix="/queue", tags=["Queue"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get queue items",
    description="Returns items in the queue with cursor pagination.",
    operation_id="get_queue",
)
def get_queue(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.QUEUE_READ)),
    service: IQueueQueryService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_queue(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )

@router.post(
    "",
    response_model=SuccessResponse[dict],
    summary="Create queue item",
    description="Add a new item to the queue.",
    operation_id="create_queue_item",
)
def create_queue_item(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.QUEUE_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IQueueQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.add_to_queue(payload)
    return SuccessResponse(data=data)

@router.delete(
    "/{item_id}",
    response_model=SuccessResponse[dict],
    summary="Delete queue item",
    description="Remove an item from the queue.",
    operation_id="delete_queue_item",
)
def delete_queue_item(
    item_id: str,
    admin: dict = Depends(requires_permission(Permission.QUEUE_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IQueueQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.remove_from_queue(item_id)
    return SuccessResponse(data=data)

@router.post(
    "/{item_id}/retry",
    response_model=SuccessResponse[dict],
    summary="Retry queue item",
    description="Retry a failed item in the queue.",
    operation_id="retry_queue_item",
)
def retry_queue_item(
    item_id: str,
    admin: dict = Depends(requires_permission(Permission.QUEUE_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IQueueQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.retry_queue_item(item_id)
    return SuccessResponse(data=data)

@router.post(
    "/{item_id}/cancel",
    response_model=SuccessResponse[dict],
    summary="Cancel queue item",
    description="Cancel a pending or active item in the queue.",
    operation_id="cancel_queue_item",
)
def cancel_queue_item(
    item_id: str,
    admin: dict = Depends(requires_permission(Permission.QUEUE_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IQueueQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.cancel_queue_item(item_id)
    return SuccessResponse(data=data)
