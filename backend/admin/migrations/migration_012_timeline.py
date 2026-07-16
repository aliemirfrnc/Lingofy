import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            metadata_json TEXT,
            created_at REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_user_timeline_user ON user_timeline(user_id, created_at DESC)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            admin_id INTEGER,
            target_type TEXT,
            target_id TEXT,
            changes_json TEXT,
            ip_address TEXT,
            created_at REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_events_created ON audit_events(created_at DESC)')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS audit_events')
    # Intentionally skipping DROP for user_timeline as it was in migration_001
