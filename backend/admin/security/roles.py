from enum import Enum

class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"
    FINANCE = "FINANCE"
    AI_ENGINEER = "AI_ENGINEER"
    CONTENT_MANAGER = "CONTENT_MANAGER"
    READ_ONLY = "READ_ONLY"

# Hardcoded base roles for initial setup. Real mappings will be stored in DB.
DEFAULT_ROLE_PERMISSIONS = {
    AdminRole.SUPER_ADMIN: ["*"],
    AdminRole.ADMIN: [
        "users.read", "users.write", "users.ban",
        "payments.read", "dashboard.view", "system.view"
    ],
    AdminRole.SUPPORT: [
        "users.read", "payments.read", "dashboard.view"
    ],
    AdminRole.FINANCE: [
        "payments.read", "payments.refund", "dashboard.view"
    ],
    AdminRole.AI_ENGINEER: [
        "ai.replay", "ai.prompt.publish", "system.view"
    ],
    AdminRole.CONTENT_MANAGER: [
        "content.write"
    ],
    AdminRole.READ_ONLY: [
        "users.read", "payments.read", "dashboard.view", "system.view"
    ]
}
