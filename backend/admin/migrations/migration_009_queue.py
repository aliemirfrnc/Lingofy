import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS job_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            payload_json TEXT,
            status TEXT DEFAULT 'QUEUED',
            priority INTEGER DEFAULT 0,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            error_text TEXT,
            created_at REAL NOT NULL,
            scheduled_at REAL NOT NULL,
            started_at REAL,
            completed_at REAL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status, scheduled_at, priority)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS job_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            error_text TEXT,
            completed_at REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_job_hist_job_id ON job_history(job_id)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS background_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL UNIQUE,
            schedule TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            last_run REAL,
            next_run REAL
        )
    ''')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS background_jobs')
    conn.execute('DROP TABLE IF EXISTS job_history')
