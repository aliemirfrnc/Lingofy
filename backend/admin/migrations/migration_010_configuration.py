import sqlite3

def upgrade(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feature_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_enabled BOOLEAN DEFAULT 0,
            description TEXT,
            updated_at REAL NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS feature_flag_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag_id INTEGER NOT NULL REFERENCES feature_flags(id),
            previous_state BOOLEAN NOT NULL,
            new_state BOOLEAN NOT NULL,
            changed_by INTEGER,
            changed_at REAL NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS runtime_configuration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value_json TEXT NOT NULL,
            updated_at REAL NOT NULL,
            updated_by INTEGER
        )
    ''')

def downgrade(conn: sqlite3.Connection):
    conn.execute('DROP TABLE IF EXISTS runtime_configuration')
    conn.execute('DROP TABLE IF EXISTS feature_flag_history')
    conn.execute('DROP TABLE IF EXISTS feature_flags')
