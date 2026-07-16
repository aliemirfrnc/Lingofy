import logging
from typing import Callable, Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.admin.api.responses.common import ProblemDetailsResponse, ValidationErrorResponse, ValidationErrorDetail
from backend.admin.services.exceptions import (
    BusinessException,
    ValidationException,
    InfrastructureException,
    ExternalProviderException,
    BaseBusinessException,
)

logger = logging.getLogger(__name__)

def get_trace_id(request: Request) -> str | None:
    """Helper to extract trace_id from the state if available."""
    return getattr(request.state, "trace_id", None)

def setup_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers mapping to RFC7807 problem details."""

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            ValidationErrorDetail(
                loc=[str(loc) for loc in err["loc"]],
                msg=err["msg"],
                type=err["type"]
            )
            for err in exc.errors()
        ]
        
        problem = ValidationErrorResponse(
            type="https://tools.ietf.org/html/rfc4918#section-11.2",
            title="Validation Error",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The request contains invalid data.",
            instance=str(request.url.path),
            trace_id=get_trace_id(request),
            errors=errors
        )
        return JSONResponse(status_code=problem.status, content=problem.model_dump(exclude_none=True))

    @app.exception_handler(ValidationException)
    async def domain_validation_exception_handler(
        request: Request, exc: ValidationException
    ) -> JSONResponse:
        problem = ProblemDetailsResponse(
            type="about:blank",
            title="Domain Validation Failed",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
            instance=str(request.url.path),
            trace_id=get_trace_id(request),
        )
        return JSONResponse(status_code=problem.status, content=problem.model_dump(exclude_none=True))

    @app.exception_handler(BusinessException)
    async def business_exception_handler(
        request: Request, exc: BusinessException
    ) -> JSONResponse:
        problem = ProblemDetailsResponse(
            type="about:blank",
            title="Business Logic Conflict",
            status=status.HTTP_409_CONFLICT,
            detail=str(exc),
            instance=str(request.url.path),
            trace_id=get_trace_id(request),
        )
        return JSONResponse(status_code=problem.status, content=problem.model_dump(exclude_none=True))

    @app.exception_handler(InfrastructureException)
    async def infrastructure_exception_handler(
        request: Request, exc: InfrastructureException
    ) -> JSONResponse:
        logger.error(f"Infrastructure error: {exc}", exc_info=True)
        problem = ProblemDetailsResponse(
            type="about:blank",
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An infrastructure error occurred.",
            instance=str(request.url.path),
            trace_id=get_trace_id(request),
        )
        return JSONResponse(status_code=problem.status, content=problem.model_dump(exclude_none=True))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        title = "HTTP Error"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            title = "Not Found"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            title = "Permission Denied"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            title = "Unauthorized"

        problem = ProblemDetailsResponse(
            type="about:blank",
            title=title,
            status=exc.status_code,
            detail=str(exc.detail),
            instance=str(request.url.path),
            trace_id=get_trace_id(request),
        )
        return JSONResponse(status_code=problem.status, content=problem.model_dump(exclude_none=True))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        problem = ProblemDetailsResponse(
            type="about:blank",
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
            instance=str(request.url.path),
            trace_id=get_trace_id(request),
        )
        return JSONResponse(status_code=problem.status, content=problem.model_dump(exclude_none=True))
