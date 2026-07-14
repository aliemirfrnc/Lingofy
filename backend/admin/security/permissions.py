from enum import Enum

class Permission(str, Enum):
    USERS_READ = "users.read"
    USERS_WRITE = "users.write"
    USERS_DELETE = "users.delete"
    USERS_BAN = "users.ban"
    
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

def has_permission(user_permissions: list[str], required_permission: str) -> bool:
    if Permission.ALL.value in user_permissions:
        return True
    return required_permission in user_permissions
