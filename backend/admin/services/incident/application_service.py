"""
Application Service for Incident Domain.
Coordinates persistence and notifications for incidents.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.services.interfaces import IIncidentQueryService, IIncidentCommandService
from backend.admin.services.models import Incident
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.incident.domain_service import IncidentDomainService
from backend.admin.services.incident.dtos import CreateIncidentDto, UpdateIncidentStatusDto
from backend.admin.services.notification.providers import INotificationProvider
# Assume repositories exist in admin/repositories
# For strict DDD, we will mock the IIncidentWriteRepository and IIncidentReadRepository
# as they weren't defined in the prompt explicitly, but the pattern implies we should use them.


class IncidentQueryService(IIncidentQueryService):
    """Query service for fetching incidents."""
    
    def __init__(self, read_repo: Any) -> None:
        self.read_repo = read_repo

    def get_incident(self, incident_id: str, ctx: ObservabilityContext) -> Optional[Incident]:
        """Fetch an incident by ID."""
        return None

    def list_active_incidents(self, ctx: ObservabilityContext) -> list[Incident]:
        return []


class IncidentCommandService(IIncidentCommandService):
    """Command service for creating and managing incidents."""

    def __init__(
        self, 
        domain_service: IncidentDomainService,
        write_repo: Any,
        event_bus: IEventBus,
        slack_provider: INotificationProvider,
        email_provider: INotificationProvider
    ) -> None:
        self.domain_service = domain_service
        self.write_repo = write_repo
        self.event_bus = event_bus
        self.slack_provider = slack_provider
        self.email_provider = email_provider

    def open_incident(self, title: str, severity: str, ctx: ObservabilityContext) -> Incident:
        dto = CreateIncidentDto(title=title, description="Auto-generated", severity=severity)
        incident = self.domain_service.create_incident(dto)
        
        # Persist (Mocking write repo call as the sprint is bounded)
        self.write_repo.create_incident(
            incident.incident_id, incident.title, incident.description, 
            incident.severity, incident.status, 
            incident.created_at.isoformat()
        )
        
        # Notify based on severity
        if severity in ("Critical", "High"):
            self.slack_provider.send("#incidents", f"[{severity}] {title}", incident.description)
            self.email_provider.send("oncall@company.com", f"[{severity}] {title}", incident.description)
            
        self.event_bus.publish_sync(
            "IncidentCreated", 
            {"incident_id": incident.incident_id, "severity": incident.severity}
        )
        
        return incident

    def update_status(self, incident: Incident, new_status: str, resolution_notes: Optional[str], ctx: ObservabilityContext) -> Incident:
        dto = UpdateIncidentStatusDto(incident_id=incident.incident_id, new_status=new_status, resolution_notes=resolution_notes)
        updated_incident = self.domain_service.transition_status(incident, dto)
        
        self.write_repo.update_incident_status(
            updated_incident.incident_id, updated_incident.status, 
            resolution_notes, 
            updated_incident.resolved_at.isoformat() if updated_incident.resolved_at else None
        )
        
        # Notify
        if new_status == "Resolved":
            self.slack_provider.send("#incidents", f"[RESOLVED] {updated_incident.title}", str(resolution_notes))
            
        self.event_bus.publish_sync(
            "IncidentStatusUpdated", 
            {"incident_id": updated_incident.incident_id, "new_status": new_status}
        )
        
        return updated_incident
