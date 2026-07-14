import sqlite3

def upgrade(conn: sqlite3.Connection):
    """
    Creates permission and role tables for the new security layer.
    """
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_role_permissions (
            role_id INTEGER NOT NULL REFERENCES admin_roles(id) ON DELETE CASCADE,
            permission_id INTEGER NOT NULL REFERENCES admin_permissions(id) ON DELETE CASCADE,
            PRIMARY KEY (role_id, permission_id)
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_user_roles (
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role_id INTEGER NOT NULL REFERENCES admin_roles(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, role_id)
        )
    ''')

def downgrade(conn: sqlite3.Connection):
    pass
