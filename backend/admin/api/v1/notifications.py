from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import INotificationCommandService
from backend.admin.api.dependencies.idempotency import verify_idempotency_key

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get notifications",
    description="Returns a list of notifications with cursor pagination.",
    operation_id="get_notifications",
)
def get_notifications(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.NOTIFICATION_READ)),
    service: INotificationCommandService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_notifications(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )

@router.post(
    "",
    response_model=SuccessResponse[dict],
    summary="Send notification",
    description="Send a new notification.",
    operation_id="send_notification",
)
def send_notification(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.NOTIFICATION_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: INotificationCommandService = Depends()
) -> SuccessResponse[dict]:
    data = service.send_notification(payload)
    return SuccessResponse(data=data)

@router.get(
    "/history",
    response_model=CursorResponse[dict],
    summary="Get notification history",
    description="Returns notification history with cursor pagination.",
    operation_id="get_notification_history",
)
def get_notification_history(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.NOTIFICATION_READ)),
    service: INotificationCommandService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_notification_history(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )
