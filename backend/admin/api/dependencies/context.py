from fastapi import Request
from backend.admin.services.providers import ObservabilityContext

def get_observability_context(request: Request) -> ObservabilityContext:
    """Dependency to extract ObservabilityContext from request state."""
    trace_id = getattr(request.state, "trace_id", "unknown")
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Optional fields
    # In a real app we would get user_id from auth token context
    user_id = None
    
    return ObservabilityContext(
        trace_id=trace_id,
        correlation_id=correlation_id,
        request_id=request_id,
        user_id=user_id,
        operation=request.url.path
    )
