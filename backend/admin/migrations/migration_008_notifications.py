import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notification_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            payload_json TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at REAL NOT NULL,
            scheduled_for REAL,
            processed_at REAL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_notif_queue_status ON notification_queue(status, scheduled_for)')

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
    conn.execute('CREATE INDEX IF NOT EXISTS idx_notif_hist_target ON notifications_history(target_type, target_id)')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS notification_queue')
    # Intentionally leaving notifications_history to avoid dropping existing tables from older migrations
