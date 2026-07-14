import sqlite3

from backend.admin.security.permissions import Permission
from backend.admin.security.roles import DEFAULT_ROLE_PERMISSIONS

def upgrade(conn: sqlite3.Connection):
    for role, permissions in DEFAULT_ROLE_PERMISSIONS.items():
        conn.execute("INSERT OR IGNORE INTO admin_roles (name, description) VALUES (?, ?)", (role.value, f"Built-in {role.value} role"))
        for permission in permissions:
            conn.execute("INSERT OR IGNORE INTO admin_permissions (name, description) VALUES (?, ?)", (permission, f"Built-in permission {permission}"))
            conn.execute("""INSERT OR IGNORE INTO admin_role_permissions (role_id, permission_id)
                SELECT r.id, p.id FROM admin_roles r, admin_permissions p WHERE r.name = ? AND p.name = ?""", (role.value, permission))
    # Existing administrators are migrated deterministically; no authorization fallback remains.
    conn.execute("""INSERT OR IGNORE INTO admin_user_roles (user_id, role_id)
        SELECT u.id, r.id FROM users u JOIN admin_roles r ON r.name = u.role
        WHERE u.role <> 'USER'""")

def downgrade(conn: sqlite3.Connection):
    raise RuntimeError("Security seed migrations are intentionally irreversible")
