# Database Schema (Operations Console Extensions)

This document contains the newly added tables from Sprint 4A (Infrastructure). These tables are isolated to the `backend/admin/migrations/` system. Existing tables are NOT affected.

## 1. Metrics (`migration_007_metrics.py`)
- `operations_metrics`
- `provider_metrics`

## 2. Notifications (`migration_008_notifications.py`)
- `notification_queue`
- `notifications_history`

## 3. Queue (`migration_009_queue.py`)
- `job_queue`
- `job_history`
- `background_jobs`

## 4. Configuration (`migration_010_configuration.py`)
- `feature_flags`
- `feature_flag_history`
- `runtime_configuration`

## 5. Incidents (`migration_011_incidents.py`)
- `incident_reports`

## 6. Timeline (`migration_012_timeline.py`)
- `user_timeline`
- `audit_events`

## 7. Observability (`migration_013_observability.py`)
- `telemetry_events`
- `request_logs`
- `system_snapshots`
- `health_snapshots`

## 8. Exports (`migration_014_exports.py`)
- `exports`
- `export_jobs`

## Entity Relationship Diagram (Operations Backend)

```mermaid
erDiagram
    operations_metrics {
        int id PK
        string metric_name
        float value
    }
    notification_queue {
        int id PK
        string type
        string status
    }
    job_queue {
        int id PK
        string job_name
        string status
    }
    incident_reports {
        int id PK
        string title
        string severity
    }
    telemetry_events {
        int id PK
        string name
        string trace_id
    }
    feature_flags {
        int id PK
        string name
        boolean is_enabled
    }
    user_timeline {
        int id PK
        int user_id
        string event_type
    }
    
    notification_queue ||--o{ notifications_history : logs
    job_queue ||--o{ job_history : logs
    feature_flags ||--o{ feature_flag_history : logs
```

*These tables utilize cursor pagination internally and avoid `OFFSET`. For dependency relations, refer to the individual migration files.*
