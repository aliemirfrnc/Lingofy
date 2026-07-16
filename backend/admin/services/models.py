"""
Immutable domain models for Operations Backend Business Services.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass(frozen=True)
class MetricsSnapshot:
    """Immutable snapshot of calculated metrics."""
    dau: int
    wau: int
    mau: int
    stickiness: float
    retention_rate: float
    premium_conversion_rate: float
    free_conversion_rate: float
    churn_rate: float
    avg_session_duration_sec: float
    avg_translation_count: float
    avg_pronunciation_count: float
    avg_ai_requests: float
    avg_response_time_ms: float
    provider_usage: Dict[str, int]
    cache_hit_rate: float
    failure_rate: float
    estimated_ai_cost: float
    trends: Dict[str, float]
    calculated_at: datetime


@dataclass(frozen=True)
class HealthDependency:
    """Immutable status of a single health dependency."""
    name: str
    status: str  # 'Healthy', 'Degraded', 'Unhealthy', 'Critical'
    latency_ms: Optional[float]
    error: Optional[str]


@dataclass(frozen=True)
class HealthSnapshot:
    """Immutable health score and levels."""
    score: int  # 0-100
    level: str  # 'Healthy', 'Degraded', 'Unhealthy', 'Critical'
    dependencies: List[HealthDependency]
    evaluated_at: datetime


@dataclass(frozen=True)
class QueueJob:
    """Immutable domain representation of a queue job."""
    job_id: str
    queue_name: str
    status: str
    priority: int
    payload: Dict[str, Any]
    created_at: datetime
    scheduled_for: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
    retries: int


@dataclass(frozen=True)
class Incident:
    """Immutable incident domain model."""
    incident_id: str
    title: str
    severity: str  # 'Critical', 'High', 'Medium', 'Low'
    status: str    # 'Open', 'Investigating', 'Monitoring', 'Resolved', 'Closed'
    created_at: datetime
    resolved_at: Optional[datetime]
    description: Optional[str]


@dataclass(frozen=True)
class FeatureFlag:
    """Immutable feature flag domain model."""
    name: str
    is_enabled: bool
    version: int
    updated_at: datetime
    targeting_rules: Dict[str, Any]


@dataclass(frozen=True)
class RuntimeConfiguration:
    """Immutable runtime configuration domain model."""
    version: int
    settings: Dict[str, Any]
    updated_at: datetime


@dataclass(frozen=True)
class ExportJob:
    """Immutable export job domain model."""
    export_id: str
    format: str  # 'CSV', 'JSON', 'XLSX'
    status: str
    requested_at: datetime
    completed_at: Optional[datetime]
    download_url: Optional[str]


@dataclass(frozen=True)
class AggregationSnapshot:
    """Immutable metrics aggregation."""
    granularity: str  # 'Hourly', 'Daily', 'Weekly', 'Monthly'
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, float]
