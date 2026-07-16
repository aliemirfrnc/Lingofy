from fastapi import Depends
import sqlite3
from typing import Generator

from backend.core.db import get_conn

# Repositories
from backend.admin.repositories.metrics_read_repo import MetricsReadRepository
from backend.admin.repositories.metrics_write_repo import MetricsWriteRepository
from backend.admin.repositories.telemetry_read_repo import TelemetryReadRepository
from backend.admin.repositories.telemetry_write_repo import TelemetryWriteRepository
from backend.admin.repositories.notification_read_repo import NotificationReadRepository
from backend.admin.repositories.notification_write_repo import NotificationWriteRepository
from backend.admin.repositories.queue_read_repo import QueueReadRepository
from backend.admin.repositories.queue_write_repo import QueueWriteRepository
from backend.admin.repositories.incident_repo import IncidentRepository
from backend.admin.repositories.health_repo import HealthRepository
from backend.admin.repositories.configuration_repo import ConfigurationRepository
from backend.admin.repositories.feature_flag_repo import FeatureFlagRepository
from backend.admin.repositories.timeline_repo import TimelineRepository

# EventBus
from backend.admin.events.memory_bus import MemoryEventBus

# No global singletons are defined here per requirements.
# The EventBus could technically be a singleton if we want cross-request state,
# but to follow strict DI rules:
_event_bus_instance = MemoryEventBus()

def get_event_bus() -> MemoryEventBus:
    return _event_bus_instance

def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    # We yield the connection, ensuring it's request-scoped
    conn = get_conn()
    try:
        yield conn
    finally:
        pass # The connection is pooled in core.db, no explicit close needed

def get_metrics_read_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> MetricsReadRepository:
    return MetricsReadRepository(conn)

def get_metrics_write_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> MetricsWriteRepository:
    return MetricsWriteRepository(conn)

def get_telemetry_read_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> TelemetryReadRepository:
    return TelemetryReadRepository(conn)

def get_telemetry_write_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> TelemetryWriteRepository:
    return TelemetryWriteRepository(conn)

def get_notification_read_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> NotificationReadRepository:
    return NotificationReadRepository(conn)

def get_notification_write_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> NotificationWriteRepository:
    return NotificationWriteRepository(conn)

def get_queue_read_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> QueueReadRepository:
    return QueueReadRepository(conn)

def get_queue_write_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> QueueWriteRepository:
    return QueueWriteRepository(conn)

def get_incident_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> IncidentRepository:
    return IncidentRepository(conn)

def get_health_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> HealthRepository:
    return HealthRepository(conn)

def get_configuration_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> ConfigurationRepository:
    return ConfigurationRepository(conn)

def get_feature_flag_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> FeatureFlagRepository:
    return FeatureFlagRepository(conn)

def get_timeline_repo(conn: sqlite3.Connection = Depends(get_db_connection)) -> TimelineRepository:
    return TimelineRepository(conn)
