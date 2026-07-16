import pytest
import sqlite3
import os
from backend.admin.migrations.manager import initialize_admin_schema
from backend.core.db import _LOCK, DATABASE_PATH

@pytest.fixture
def mock_db_conn(monkeypatch):
    """Provide a fresh in-memory database for migration tests."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    
    # Create mock core tables that admin migrations expect
    conn.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, created_at REAL, role TEXT)")
    conn.execute("CREATE TABLE user_sessions(id INTEGER PRIMARY KEY, user_id INTEGER, is_active INTEGER)")
    conn.execute("CREATE TABLE job_queue(id INTEGER PRIMARY KEY, status TEXT, scheduled_at REAL, priority INTEGER)")
    conn.execute("CREATE TABLE admin_audit_logs(id INTEGER PRIMARY KEY, created_at REAL)")
    conn.execute("CREATE TABLE ai_conversations(id INTEGER PRIMARY KEY, created_at REAL)")
    conn.execute("CREATE TABLE user_timeline(id INTEGER PRIMARY KEY, user_id INTEGER, created_at REAL, event_type TEXT, metadata_json TEXT)")
    conn.execute("CREATE TABLE payments(id INTEGER PRIMARY KEY, created_at REAL)")
    conn.execute("CREATE TABLE spotify_accounts(user_id INTEGER PRIMARY KEY, access_token TEXT, refresh_token TEXT)")
    
    monkeypatch.setattr("backend.admin.migrations.manager.get_conn", lambda: conn)
    monkeypatch.setattr("backend.admin.migrations.manager.get_lock", lambda: _LOCK)
    
    yield conn
    conn.close()

def test_all_migrations_run_successfully(mock_db_conn):
    # This should run migration 001 through 014 without syntax errors
    initialize_admin_schema()
    
    # Verify some of the newly added tables from 007-014 exist
    cursor = mock_db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        "operations_metrics",
        "provider_metrics",
        "notification_queue",
        "job_queue",
        "feature_flags",
        "incident_reports",
        "user_timeline",
        "audit_events",
        "telemetry_events",
        "exports",
    ]
    
    for t in expected_tables:
        assert t in tables, f"Expected table {t} was not created."

def test_migration_idempotency(mock_db_conn):
    # Running it twice shouldn't fail
    initialize_admin_schema()
    initialize_admin_schema()
