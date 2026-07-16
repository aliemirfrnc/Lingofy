"""
Service Interfaces for CQRS Operations Business Services.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any

from backend.admin.services.models import (
    MetricsSnapshot, HealthSnapshot, QueueJob,
    Incident, FeatureFlag, RuntimeConfiguration,
    ExportJob, AggregationSnapshot
)
from backend.admin.services.providers import ObservabilityContext


# --- METRICS ---
class IMetricsQueryService(ABC):
    @abstractmethod
    def get_latest_snapshot(self, ctx: ObservabilityContext) -> MetricsSnapshot:
        pass


class IMetricsCommandService(ABC):
    @abstractmethod
    def trigger_calculation(self, ctx: ObservabilityContext) -> MetricsSnapshot:
        pass


# --- HEALTH ---
class IHealthQueryService(ABC):
    @abstractmethod
    def check_health(self, ctx: ObservabilityContext) -> HealthSnapshot:
        pass


# --- QUEUE ---
class IQueueQueryService(ABC):
    @abstractmethod
    def get_job(self, job_id: str, ctx: ObservabilityContext) -> Optional[QueueJob]:
        pass


class IQueueCommandService(ABC):
    @abstractmethod
    def create_job(self, queue_name: str, payload: dict, priority: int, ctx: ObservabilityContext) -> QueueJob:
        pass


# --- NOTIFICATION ---
class INotificationCommandService(ABC):
    @abstractmethod
    def send_notification(self, type: str, payload: dict, ctx: ObservabilityContext) -> bool:
        pass


# --- INCIDENT ---
class IIncidentQueryService(ABC):
    @abstractmethod
    def get_incident(self, incident_id: str, ctx: ObservabilityContext) -> Optional[Incident]:
        pass


class IIncidentCommandService(ABC):
    @abstractmethod
    def open_incident(self, title: str, severity: str, ctx: ObservabilityContext) -> Incident:
        pass


# --- FEATURE FLAGS ---
class IFeatureFlagQueryService(ABC):
    @abstractmethod
    def get_flag(self, name: str, ctx: ObservabilityContext) -> Optional[FeatureFlag]:
        pass


class IFeatureFlagCommandService(ABC):
    @abstractmethod
    def enable_flag(self, name: str, ctx: ObservabilityContext) -> FeatureFlag:
        pass


# --- RUNTIME CONFIGURATION ---
class IRuntimeConfigurationQueryService(ABC):
    @abstractmethod
    def get_configuration(self, ctx: ObservabilityContext) -> RuntimeConfiguration:
        pass


class IRuntimeConfigurationCommandService(ABC):
    @abstractmethod
    def update_configuration(self, settings: dict, ctx: ObservabilityContext) -> RuntimeConfiguration:
        pass


# --- EXPORT ---
class IExportQueryService(ABC):
    @abstractmethod
    def get_export_job(self, export_id: str, ctx: ObservabilityContext) -> Optional[ExportJob]:
        pass


class IExportCommandService(ABC):
    @abstractmethod
    def request_export(self, format: str, params: dict, ctx: ObservabilityContext) -> ExportJob:
        pass


# --- AGGREGATION ---
class IAggregationQueryService(ABC):
    @abstractmethod
    def get_aggregation(self, granularity: str, ctx: ObservabilityContext) -> AggregationSnapshot:
        pass


class IAggregationCommandService(ABC):
    @abstractmethod
    def run_aggregation(self, granularity: str, ctx: ObservabilityContext) -> AggregationSnapshot:
        pass
