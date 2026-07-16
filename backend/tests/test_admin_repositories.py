import pytest
import sqlite3
from backend.admin.migrations.manager import initialize_admin_schema
from backend.admin.repositories.metrics_write_repo import MetricsWriteRepository
from backend.admin.repositories.metrics_read_repo import MetricsReadRepository
from backend.admin.repositories.queue_write_repo import QueueWriteRepository
from backend.admin.repositories.queue_read_repo import QueueReadRepository

@pytest.fixture
def db_conn(monkeypatch):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    
    # Create mock core tables
    conn.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, created_at REAL, role TEXT)")
    conn.execute("CREATE TABLE user_sessions(id INTEGER PRIMARY KEY, user_id INTEGER, is_active INTEGER)")
    conn.execute("CREATE TABLE admin_audit_logs(id INTEGER PRIMARY KEY, created_at REAL)")
    conn.execute("CREATE TABLE ai_conversations(id INTEGER PRIMARY KEY, created_at REAL)")
    conn.execute("CREATE TABLE user_timeline(id INTEGER PRIMARY KEY, user_id INTEGER, created_at REAL, event_type TEXT, metadata_json TEXT)")
    conn.execute("CREATE TABLE payments(id INTEGER PRIMARY KEY, created_at REAL)")
    conn.execute("CREATE TABLE spotify_accounts(user_id INTEGER PRIMARY KEY, access_token TEXT, refresh_token TEXT)")

    monkeypatch.setattr("backend.admin.migrations.manager.get_conn", lambda: conn)
    initialize_admin_schema()
    
    yield conn
    conn.close()

def test_metrics_repository(db_conn):
    writer = MetricsWriteRepository(db_conn)
    reader = MetricsReadRepository(db_conn)

    # Insert single
    writer.insert_operation_metric("test_metric", 1.5, "{}")
    
    # Insert batch
    writer.batch_insert_operation_metrics([
        {"metric_name": "test_batch_1", "value": 2.0},
        {"metric_name": "test_batch_2", "value": 3.0}
    ])

    # Read
    results = reader.get_operations_metrics(limit=10)
    assert len(results) == 3
    
    # Cursor pagination
    cursor_id = results[0]["id"] # Since it's ordered by DESC, this is the largest ID
    paged = reader.get_operations_metrics(limit=10, cursor=cursor_id)
    assert len(paged) == 2

def test_queue_repository(db_conn):
    writer = QueueWriteRepository(db_conn)
    reader = QueueReadRepository(db_conn)

    job_id1 = writer.enqueue_job("job1", "{}", priority=10)
    job_id2 = writer.enqueue_job("job2", "{}", priority=5)

    jobs = reader.get_queued_jobs()
    assert len(jobs) == 2
    assert jobs[0]["job_name"] == "job1" # higher priority

    writer.update_job_status(job_id1, "COMPLETED")
    writer.insert_job_history(job_id1, "COMPLETED")
    
    pending = reader.get_queued_jobs()
    assert len(pending) == 1

    history = reader.get_job_history()
    assert len(history) == 1
    assert history[0]["status"] == "COMPLETED"
