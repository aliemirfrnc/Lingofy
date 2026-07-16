from enum import Enum

class Permission(str, Enum):
    # User Management
    USERS_READ = "users.read"
    USERS_WRITE = "users.write"
    USERS_DELETE = "users.delete"
    USERS_BAN = "users.ban"

    # Operations
    DASHBOARD_READ = "dashboard.read"
    METRICS_READ = "metrics.read"
    HEALTH_READ = "health.read"
    QUEUE_READ = "queue.read"
    QUEUE_WRITE = "queue.write"
    INCIDENT_READ = "incident.read"
    INCIDENT_WRITE = "incident.write"
    FEATURE_FLAG_READ = "feature_flag.read"
    FEATURE_FLAG_WRITE = "feature_flag.write"
    CONFIGURATION_READ = "configuration.read"
    CONFIGURATION_WRITE = "configuration.write"
    NOTIFICATION_READ = "notification.read"
    NOTIFICATION_WRITE = "notification.write"
    EXPORT_READ = "export.read"
    EXPORT_WRITE = "export.write"
    TIMELINE_READ = "timeline.read"
    PROVIDER_STATUS_READ = "provider_status.read"
    
    # Legacy
    PAYMENTS_READ = "payments.read"
    PAYMENTS_REFUND = "payments.refund"
    AI_REPLAY = "ai.replay"
    AI_PROMPT_PUBLISH = "ai.prompt.publish"
    SYSTEM_VIEW = "system.view"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_RESTORE = "system.restore"
    FEATURE_TOGGLE = "feature.toggle"
    DASHBOARD_VIEW = "dashboard.view"
    
    ALL = "*" # Wildcard permission

def has_permission(user_permissions: list[str], required_permission: Permission) -> bool:
    if Permission.ALL.value in user_permissions:
        return True
    return required_permission.value in user_permissions
