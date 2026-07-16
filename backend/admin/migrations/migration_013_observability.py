import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS telemetry_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            span_id TEXT,
            name TEXT NOT NULL,
            attributes_json TEXT,
            timestamp REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_telemetry_trace ON telemetry_events(trace_id)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            correlation_id TEXT,
            route TEXT,
            method TEXT,
            status_code INTEGER,
            latency_ms REAL,
            user_id INTEGER,
            timestamp REAL NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_req_logs_ts ON request_logs(timestamp DESC)')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS system_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            active_connections INTEGER,
            timestamp REAL NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS health_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            status TEXT NOT NULL,
            details_json TEXT,
            timestamp REAL NOT NULL
        )
    ''')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS health_snapshots')
    conn.execute('DROP TABLE IF EXISTS system_snapshots')
    conn.execute('DROP TABLE IF EXISTS request_logs')
    conn.execute('DROP TABLE IF EXISTS telemetry_events')
