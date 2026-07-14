import sqlite3

def upgrade(conn: sqlite3.Connection):
    """
    Creates indexes specifically for cursor pagination and fast admin queries.
    """
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_job_queue_status_scheduled ON job_queue(status, scheduled_at)",
        "CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_created_at ON admin_audit_logs(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_at ON ai_conversations(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_user_timeline_user_id_created_at ON user_timeline(user_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at DESC)"
    ]
    for idx in indexes:
        conn.execute(idx)

def downgrade(conn: sqlite3.Connection):
    pass
