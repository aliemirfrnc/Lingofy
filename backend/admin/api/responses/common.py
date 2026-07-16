from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""
    data: T
    meta: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class CursorResponse(BaseModel, Generic[T]):
    """Standard cursor pagination response."""
    data: List[T]
    cursor: Optional[str] = Field(None, description="Current cursor string")
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page")
    previous_cursor: Optional[str] = Field(None, description="Cursor for the previous page")
    limit: int = Field(..., description="Maximum number of items per page")
    total_count: Optional[int] = Field(None, description="Total number of items if calculable")

    model_config = ConfigDict(populate_by_name=True)


class ProblemDetailsResponse(BaseModel):
    """
    RFC 7807 compliant problem details response for errors.
    """
    type: str = Field(
        default="about:blank", 
        description="A URI reference that identifies the problem type."
    )
    title: str = Field(..., description="A short, human-readable summary of the problem type.")
    status: int = Field(..., description="The HTTP status code.")
    detail: str = Field(..., description="A human-readable explanation specific to this occurrence of the problem.")
    instance: Optional[str] = Field(None, description="A URI reference that identifies the specific occurrence of the problem.")
    trace_id: Optional[str] = Field(None, description="Correlation or trace ID for debugging.")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional properties.")


class ValidationErrorDetail(BaseModel):
    """Detail for a specific field validation error."""
    loc: List[str] = Field(..., description="Location of the validation error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(ProblemDetailsResponse):
    """
    Validation error response extending ProblemDetailsResponse.
    """
    errors: List[ValidationErrorDetail] = Field(
        default_factory=list, 
        description="List of validation errors"
    )

