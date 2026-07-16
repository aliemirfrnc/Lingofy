import time
import uuid
import logging
from contextvars import ContextVar
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)

# Context vars for Observability and Audit
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="")
user_id_ctx: ContextVar[Optional[int]] = ContextVar("user_id", default=None)
user_permissions_ctx: ContextVar[list[str]] = ContextVar("user_permissions", default=[])

class AuditObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically generate and attach:
    RequestId, CorrelationId, TraceId, Duration, UserId, Permission, 
    StatusCode, Endpoint, HTTP Method, IPAddress, UserAgent
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        
        # Extract or generate IDs
        req_id = str(uuid.uuid4())
        corr_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        # Set context vars
        request_id_ctx.set(req_id)
        correlation_id_ctx.set(corr_id)
        trace_id_ctx.set(trace_id)
        
        # Attach to request state for other parts
        request.state.request_id = req_id
        request.state.correlation_id = corr_id
        request.state.trace_id = trace_id
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Security Hardening: Never return Stack Trace directly in responses (Handled by Global Exception Handler)
            
            # Extract client info
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "unknown")
            endpoint = str(request.url.path)
            method = request.method
            
            user_id = user_id_ctx.get()
            
            audit_log = {
                "request_id": req_id,
                "correlation_id": corr_id,
                "trace_id": trace_id,
                "duration_ms": duration_ms,
                "user_id": user_id,
                "status_code": status_code,
                "endpoint": endpoint,
                "method": method,
                "ip_address": client_ip,
                "user_agent": user_agent,
            }
            
            # Log automatically without manual logging in endpoints
            logger.info("Admin API Audit Log", extra={"audit_context": audit_log})
            
            # Idempotency and Trace headers
            if "response" in locals():
                response.headers["X-Request-ID"] = req_id
                response.headers["X-Correlation-ID"] = corr_id
                response.headers["X-Trace-ID"] = trace_id
                
                # Security Headers (Security Hardening Phase 18)
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
