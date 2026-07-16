import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            export_type TEXT NOT NULL,
            file_format TEXT NOT NULL,
            status TEXT DEFAULT 'PROCESSING',
            file_path TEXT,
            error_text TEXT,
            created_at REAL NOT NULL,
            completed_at REAL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_exports_status ON exports(status)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS export_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            query_json TEXT,
            status TEXT DEFAULT 'QUEUED',
            file_url TEXT,
            created_at REAL NOT NULL,
            completed_at REAL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_export_jobs_status ON export_jobs(status)')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS export_jobs')
    # Intentionally skipping DROP for exports as it was in migration_001
