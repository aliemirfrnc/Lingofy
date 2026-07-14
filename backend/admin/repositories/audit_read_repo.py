from typing import Dict, Any, List, Optional
import sqlite3
from backend.core.db import get_conn

class AuditReadRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def get_audit_logs_paginated(self, cursor_id: Optional[int], limit: int = 50, action_filter: str = None) -> List[Dict[str, Any]]:
        query = "SELECT id, admin_id, action, resource, target_id, ip_address, created_at FROM admin_audit_logs"
        params = []
        conditions = []

        if action_filter:
            conditions.append("action = ?")
            params.append(action_filter)

        if cursor_id is not None:
            conditions.append("id < ?")
            params.append(cursor_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "admin_id": row[1],
                "action": row[2],
                "resource": row[3],
                "target_id": row[4],
                "ip_address": row[5],
                "created_at": row[6]
            })
        return logs
