from typing import Dict, Any, Optional
import sqlite3
import time
from backend.core.db import get_conn

class AuditWriteRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def log_action(self, admin_id: int, action: str, resource: str, target_id: Optional[str] = None, diff_before: Optional[str] = None, diff_after: Optional[str] = None, ip_address: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO admin_audit_logs 
            (admin_id, action, resource, target_id, diff_before, diff_after, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, action, resource, target_id, diff_before, diff_after, ip_address, time.time()))
        return cursor.lastrowid
