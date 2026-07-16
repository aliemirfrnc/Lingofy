"""
Domain Service for Incident.
Pure business logic, no I/O.
"""
from backend.admin.services.models import Incident
from backend.admin.services.providers import ISystemClock, IIdGenerator
from backend.admin.services.exceptions import IncidentException
from backend.admin.services.incident.dtos import CreateIncidentDto, UpdateIncidentStatusDto


class IncidentDomainService:
    """Manages incident lifecycle transitions and rules."""

    VALID_SEVERITIES = {"Critical", "High", "Medium", "Low"}
    VALID_STATUSES = {"Open", "Investigating", "Mitigated", "Resolved"}
    
    # Valid forward transitions
    TRANSITIONS = {
        "Open": {"Investigating", "Mitigated", "Resolved"},
        "Investigating": {"Mitigated", "Resolved"},
        "Mitigated": {"Resolved"},
        "Resolved": set()  # Terminal state
    }

    def __init__(self, clock: ISystemClock, id_gen: IIdGenerator) -> None:
        self.clock = clock
        self.id_gen = id_gen

    def create_incident(self, dto: CreateIncidentDto) -> Incident:
        """Create a new incident from DTO."""
        if not dto.title or not dto.description:
            raise IncidentException("Title and description are required.")
            
        if dto.severity not in self.VALID_SEVERITIES:
            raise IncidentException(f"Invalid severity: {dto.severity}")
            
        return Incident(
            incident_id=self.id_gen.generate(),
            title=dto.title,
            severity=dto.severity,
            status="Open",
            created_at=self.clock.now(),
            resolved_at=None,
            description=dto.description
        )

    def transition_status(self, incident: Incident, dto: UpdateIncidentStatusDto) -> Incident:
        """Transition incident status based on rules."""
        if dto.new_status not in self.VALID_STATUSES:
            raise IncidentException(f"Invalid status: {dto.new_status}")
            
        if dto.new_status not in self.TRANSITIONS.get(incident.status, set()):
            raise IncidentException(f"Cannot transition from {incident.status} to {dto.new_status}")
            
        resolved_at = None
        new_description = incident.description
        
        if dto.new_status == "Resolved":
            if not dto.resolution_notes and incident.severity in ("Critical", "High"):
                raise IncidentException("Resolution notes are required for Critical/High incidents.")
            resolved_at = self.clock.now()
            if dto.resolution_notes:
                new_description = f"{new_description}\n\nResolution: {dto.resolution_notes}" if new_description else f"Resolution: {dto.resolution_notes}"
            
        return Incident(
            incident_id=incident.incident_id,
            title=incident.title,
            severity=incident.severity,
            status=dto.new_status,
            created_at=incident.created_at,
            resolved_at=resolved_at,
            description=new_description
        )
