import sqlite3

def upgrade(conn: sqlite3.Connection):
    """
    Creates base tables for operations console.
    """
    # 1. Admin Notes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
            note TEXT NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    ''')

    # 2. User Tags
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tag TEXT NOT NULL,
            created_at REAL NOT NULL,
            UNIQUE(user_id, tag)
        )
    ''')

    # 3. User Sessions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            device TEXT,
            platform TEXT,
            browser TEXT,
            ip_address TEXT,
            country TEXT,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            last_active REAL NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # 4. Payment Events
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id INTEGER REFERENCES payments(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            provider_event_id TEXT,
            payload_json TEXT,
            created_at REAL NOT NULL
        )
    ''')

    # 5. Job Queue
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

    # 6. Notifications History
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notifications_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT NOT NULL,
            target_id TEXT,
            channel TEXT NOT NULL,
            title TEXT,
            message TEXT,
            status TEXT DEFAULT 'PENDING',
            error_text TEXT,
            created_at REAL NOT NULL,
            sent_at REAL
        )
    ''')

    # 7. Exports
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

    # 8. Backups
    conn.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            file_path TEXT NOT NULL,
            size_bytes INTEGER,
            checksum TEXT,
            status TEXT DEFAULT 'COMPLETED',
            created_at REAL NOT NULL
        )
    ''')

    # 9. Deployments
    conn.execute('''
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            commit_hash TEXT,
            environment TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at REAL NOT NULL
        )
    ''')

    # 10. User Timeline (Event Bus persistence for profile)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            metadata_json TEXT,
            created_at REAL NOT NULL
        )
    ''')

def downgrade(conn: sqlite3.Connection):
    pass
