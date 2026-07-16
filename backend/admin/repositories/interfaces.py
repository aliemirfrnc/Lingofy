from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IMetricsReadRepository(ABC):
    @abstractmethod
    def get_operations_metrics(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_provider_metrics(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_active_users_count(self, days: int) -> int:
        pass

    @abstractmethod
    def get_total_users_count(self) -> int:
        pass

    @abstractmethod
    def get_premium_users_count(self) -> int:
        pass

    @abstractmethod
    def get_new_users_count(self, days: int) -> int:
        pass

    @abstractmethod
    def get_churned_users_count(self, days: int) -> int:
        pass

    @abstractmethod
    def get_retained_users_count(self, days: int) -> int:
        pass

    @abstractmethod
    def get_total_session_duration_sec(self) -> float:
        pass

    @abstractmethod
    def get_total_sessions_count(self) -> int:
        pass

    @abstractmethod
    def get_total_translations_count(self) -> int:
        pass

    @abstractmethod
    def get_total_pronunciations_count(self) -> int:
        pass

    @abstractmethod
    def get_total_ai_requests_count(self) -> int:
        pass

    @abstractmethod
    def get_total_response_time_ms(self) -> float:
        pass

    @abstractmethod
    def get_provider_calls_distribution(self) -> Dict[str, int]:
        pass

    @abstractmethod
    def get_cache_hits(self) -> int:
        pass

    @abstractmethod
    def get_cache_misses(self) -> int:
        pass

    @abstractmethod
    def get_total_failures(self) -> int:
        pass

    @abstractmethod
    def get_total_operations(self) -> int:
        pass

    @abstractmethod
    def get_ai_cost_per_request(self) -> float:
        pass

class IMetricsWriteRepository(ABC):
    @abstractmethod
    def insert_operation_metric(self, metric_name: str, value: float, tags_json: Optional[str] = None) -> int:
        pass

    @abstractmethod
    def batch_insert_operation_metrics(self, metrics: List[Dict[str, Any]]) -> int:
        pass

    @abstractmethod
    def update_provider_metric(self, provider_name: str, model_name: Optional[str], request_count: int, error_count: int, latency: float) -> None:
        pass

class ITelemetryReadRepository(ABC):
    @abstractmethod
    def get_telemetry_events(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_request_logs(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

class ITelemetryWriteRepository(ABC):
    @abstractmethod
    def insert_telemetry_event(self, trace_id: Optional[str], span_id: Optional[str], name: str, attributes_json: Optional[str]) -> int:
        pass

    @abstractmethod
    def batch_insert_telemetry_events(self, events: List[Dict[str, Any]]) -> int:
        pass

    @abstractmethod
    def insert_request_log(self, request_id: str, correlation_id: Optional[str], route: str, method: str, status_code: int, latency_ms: float, user_id: Optional[int]) -> int:
        pass

class INotificationReadRepository(ABC):
    @abstractmethod
    def get_pending_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_notifications_history(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

class INotificationWriteRepository(ABC):
    @abstractmethod
    def enqueue_notification(self, type: str, payload_json: str, scheduled_for: Optional[float] = None) -> int:
        pass

    @abstractmethod
    def update_notification_status(self, notification_id: int, status: str, error_text: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def insert_history(self, target_type: str, target_id: str, channel: str, title: str, message: str, status: str) -> int:
        pass

class IQueueReadRepository(ABC):
    @abstractmethod
    def get_queued_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_job_history(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

class IQueueWriteRepository(ABC):
    @abstractmethod
    def enqueue_job(self, job_name: str, payload_json: Optional[str] = None, priority: int = 0, scheduled_at: Optional[float] = None) -> int:
        pass

    @abstractmethod
    def update_job_status(self, job_id: int, status: str, error_text: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def insert_job_history(self, job_id: int, status: str, error_text: Optional[str] = None) -> int:
        pass

class IIncidentRepository(ABC):
    @abstractmethod
    def get_incidents(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def insert_incident(self, title: str, description: str, severity: str) -> int:
        pass

    @abstractmethod
    def update_incident_status(self, incident_id: int, status: str) -> None:
        pass

class IHealthRepository(ABC):
    @abstractmethod
    def get_health_snapshots(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def insert_health_snapshot(self, service_name: str, status: str, details_json: Optional[str]) -> int:
        pass

class IConfigurationRepository(ABC):
    @abstractmethod
    def get_runtime_configuration(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_config_value(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set_config_value(self, key: str, value_json: str, admin_id: Optional[int] = None) -> None:
        pass

class IFeatureFlagRepository(ABC):
    @abstractmethod
    def get_feature_flags(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_feature_flag(self, name: str) -> Optional[bool]:
        pass

    @abstractmethod
    def set_feature_flag(self, name: str, is_enabled: bool, admin_id: Optional[int] = None) -> None:
        pass

class ITimelineRepository(ABC):
    @abstractmethod
    def get_user_timeline(self, user_id: int, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def insert_user_event(self, user_id: int, event_type: str, metadata_json: Optional[str]) -> int:
        pass

    @abstractmethod
    def get_audit_events(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def insert_audit_event(self, action: str, admin_id: Optional[int], target_type: Optional[str], target_id: Optional[str], changes_json: Optional[str], ip_address: Optional[str]) -> int:
        pass
