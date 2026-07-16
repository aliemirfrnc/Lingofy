"""
Data Transfer Objects for the Incident domain.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateIncidentDto:
    """DTO for creating an incident."""
    title: str
    description: str
    severity: str  # Critical, High, Medium, Low


@dataclass(frozen=True)
class UpdateIncidentStatusDto:
    """DTO for transitioning an incident status."""
    incident_id: str
    new_status: str  # Open, Investigating, Mitigated, Resolved
    resolution_notes: Optional[str] = None
