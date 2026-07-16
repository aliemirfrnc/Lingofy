from fastapi import APIRouter, Depends
from backend.admin.api.responses.common import SuccessResponse, CursorResponse
from backend.admin.api.dto.filters import BaseFilterDTO
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IIncidentQueryService
from backend.admin.api.dependencies.idempotency import verify_idempotency_key

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get(
    "",
    response_model=CursorResponse[dict],
    summary="Get incidents",
    description="Returns a list of incidents with cursor pagination.",
    operation_id="get_incidents",
)
def get_incidents(
    filters: BaseFilterDTO = Depends(),
    admin: dict = Depends(requires_permission(Permission.INCIDENT_READ)),
    service: IIncidentQueryService = Depends()
) -> CursorResponse[dict]:
    data, next_cursor, prev_cursor, total = service.get_incidents(filters.model_dump())
    return CursorResponse(
        data=data, cursor=filters.cursor, next_cursor=next_cursor, 
        previous_cursor=prev_cursor, limit=filters.limit, total_count=total
    )

@router.post(
    "",
    response_model=SuccessResponse[dict],
    summary="Create incident",
    description="Create a new incident.",
    operation_id="create_incident",
)
def create_incident(
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.INCIDENT_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IIncidentQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.create_incident(payload)
    return SuccessResponse(data=data)

@router.patch(
    "/{incident_id}",
    response_model=SuccessResponse[dict],
    summary="Update incident",
    description="Update an existing incident.",
    operation_id="update_incident",
)
def update_incident(
    incident_id: str,
    payload: dict,
    admin: dict = Depends(requires_permission(Permission.INCIDENT_WRITE)),
    idempotency_key: str = Depends(verify_idempotency_key),
    service: IIncidentQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.update_incident(incident_id, payload)
    return SuccessResponse(data=data)

@router.get(
    "/{incident_id}",
    response_model=SuccessResponse[dict],
    summary="Get incident details",
    description="Get details of a specific incident.",
    operation_id="get_incident_details",
)
def get_incident_details(
    incident_id: str,
    admin: dict = Depends(requires_permission(Permission.INCIDENT_READ)),
    service: IIncidentQueryService = Depends()
) -> SuccessResponse[dict]:
    data = service.get_incident(incident_id)
    return SuccessResponse(data=data)
