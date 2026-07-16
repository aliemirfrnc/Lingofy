from fastapi import APIRouter, Depends, Header, Request
from backend.admin.api.responses.common import SuccessResponse
from backend.admin.security.permissions import Permission
from backend.admin.security.authorization import requires_permission
from backend.admin.services.interfaces import IHealthQueryService

# Phase 10: Versioning
router = APIRouter(prefix="/health", tags=["Health"])

# Phase 9: OpenAPI details like summary, response, etc.
@router.get(
    "",
    response_model=SuccessResponse[dict],
    summary="Get overall system health",
    description="Returns the aggregated health status of all system components.",
    operation_id="get_health_overall",
)
def get_health(
    # Phase 3: Permission Security
    admin: dict = Depends(requires_permission(Permission.HEALTH_READ)),
    # Constructor Injection placeholder for Service
    service: IHealthQueryService = Depends()
) -> SuccessResponse[dict]:
    # Phase 5: No business logic, only Application Service call
    status = service.get_overall_health()
    
    return SuccessResponse(data=status)

@router.get(
    "/providers",
    response_model=SuccessResponse[dict],
    summary="Get providers health",
    description="Returns the health status of external providers.",
    operation_id="get_health_providers",
)
def get_providers_health(
    admin: dict = Depends(requires_permission(Permission.HEALTH_READ)),
    service: IHealthQueryService = Depends()
) -> SuccessResponse[dict]:
    status = service.get_providers_health()
    return SuccessResponse(data=status)

@router.get(
    "/system",
    response_model=SuccessResponse[dict],
    summary="Get system health",
    description="Returns the health status of core system components.",
    operation_id="get_health_system",
)
def get_system_health(
    admin: dict = Depends(requires_permission(Permission.HEALTH_READ)),
    service: IHealthQueryService = Depends()
) -> SuccessResponse[dict]:
    status = service.get_system_health()
    return SuccessResponse(data=status)

@router.get(
    "/database",
    response_model=SuccessResponse[dict],
    summary="Get database health",
    description="Returns the health status of the database.",
    operation_id="get_health_database",
)
def get_database_health(
    admin: dict = Depends(requires_permission(Permission.HEALTH_READ)),
    service: IHealthQueryService = Depends()
) -> SuccessResponse[dict]:
    status = service.get_database_health()
    return SuccessResponse(data=status)

@router.get(
    "/cache",
    response_model=SuccessResponse[dict],
    summary="Get cache health",
    description="Returns the health status of the cache system.",
    operation_id="get_health_cache",
)
def get_cache_health(
    admin: dict = Depends(requires_permission(Permission.HEALTH_READ)),
    service: IHealthQueryService = Depends()
) -> SuccessResponse[dict]:
    status = service.get_cache_health()
    return SuccessResponse(data=status)
