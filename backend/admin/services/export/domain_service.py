"""
Domain Service for Export Domain.
"""
from typing import Any
import uuid

from backend.admin.services.models import ExportJob
from backend.admin.services.providers import ISystemClock
from backend.admin.services.exceptions import ExportException
from backend.admin.services.export.dtos import RequestExportDto


class ExportDomainService:
    """Manages export business logic."""

    VALID_FORMATS = {"CSV", "JSON", "XLSX"}

    def __init__(self, clock: ISystemClock) -> None:
        self.clock = clock

    def _validate_format(self, format_type: str) -> None:
        if format_type.upper() not in self.VALID_FORMATS:
            raise ExportException(f"Unsupported export format: {format_type}. Must be one of {self.VALID_FORMATS}.")

    def create_export_job(self, dto: RequestExportDto) -> ExportJob:
        """Create a new export job from a request."""
        self._validate_format(dto.format)
        
        return ExportJob(
            export_id=str(uuid.uuid4()),
            format=dto.format.upper(),
            status="Pending",
            requested_at=self.clock.now(),
            completed_at=None,
            download_url=None
        )
