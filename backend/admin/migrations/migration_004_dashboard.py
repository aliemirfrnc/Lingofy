import sqlite3

def upgrade(conn: sqlite3.Connection):
    """
    Creates dashboard specific tables for persisting widgets and configs.
    """
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_dashboard_widgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            widget_type TEXT NOT NULL,
            config_json TEXT NOT NULL,
            position_x INTEGER DEFAULT 0,
            position_y INTEGER DEFAULT 0,
            width INTEGER DEFAULT 1,
            height INTEGER DEFAULT 1,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value_json TEXT NOT NULL,
            description TEXT,
            updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            updated_at REAL NOT NULL
        )
    ''')

def downgrade(conn: sqlite3.Connection):
    pass
