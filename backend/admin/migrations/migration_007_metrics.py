import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS operations_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            tags_json TEXT,
            timestamp REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ops_metrics_name ON operations_metrics(metric_name)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ops_metrics_ts ON operations_metrics(timestamp)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS provider_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_name TEXT NOT NULL,
            model_name TEXT,
            request_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            avg_latency REAL DEFAULT 0.0,
            timestamp REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_prov_metrics_name ON provider_metrics(provider_name, timestamp)')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS provider_metrics')
    conn.execute('DROP TABLE IF EXISTS operations_metrics')
