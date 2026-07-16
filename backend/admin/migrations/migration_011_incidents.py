import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS incident_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            created_at REAL NOT NULL,
            resolved_at REAL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incident_reports(status)')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS incident_reports')
