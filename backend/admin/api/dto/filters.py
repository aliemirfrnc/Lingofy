from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class BaseFilterDTO(BaseModel):
    """
    Standard filter DTO for list endpoints.
    Used for filtering, sorting, and cursor pagination.
    """
    search: Optional[str] = Field(None, description="Search term for text fields")
    sort: Optional[str] = Field(None, description="Field name to sort by")
    direction: Literal["asc", "desc"] = Field("desc", description="Sort direction (asc/desc)")
    
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")
    
    from_date: Optional[datetime] = Field(None, description="Filter from date (ISO-8601 UTC)")
    to_date: Optional[datetime] = Field(None, description="Filter to date (ISO-8601 UTC)")
    
    status: Optional[str] = Field(None, description="Filter by status")
    provider: Optional[str] = Field(None, description="Filter by provider name")
    
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
