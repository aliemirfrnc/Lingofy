"""
Application Service for Export Domain.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.services.interfaces import IExportQueryService, IExportCommandService
from backend.admin.services.models import ExportJob
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.export.domain_service import ExportDomainService
from backend.admin.services.export.dtos import RequestExportDto


class ExportQueryService(IExportQueryService):
    """Query service for fetching export jobs."""
    
    def __init__(self, read_repo: Any) -> None:
        self.read_repo = read_repo

    def get_export_job(self, export_id: str, ctx: ObservabilityContext) -> Optional[ExportJob]:
        """Fetch an export job by ID."""
        return None


class ExportCommandService(IExportCommandService):
    """Command service for managing export jobs."""

    def __init__(
        self, 
        domain_service: ExportDomainService,
        write_repo: Any,
        event_bus: IEventBus
    ) -> None:
        self.domain_service = domain_service
        self.write_repo = write_repo
        self.event_bus = event_bus

    def request_export(self, format: str, params: dict, ctx: ObservabilityContext) -> ExportJob:
        """Request a new export job."""
        dto = RequestExportDto(format=format, params=params)
        job = self.domain_service.create_export_job(dto)
        
        self.write_repo.save_export_job(
            job.export_id, job.format, job.status, job.requested_at.isoformat()
        )
        
        self.event_bus.publish_sync(
            "ExportRequested", 
            {
                "export_id": job.export_id, 
                "format": job.format,
                "params": dto.params
            }
        )
        
        return job
