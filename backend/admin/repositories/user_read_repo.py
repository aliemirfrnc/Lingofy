from typing import Dict, Any, List, Optional
import sqlite3
from backend.core.db import get_conn

class UserReadRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def get_users_paginated(self, cursor_id: Optional[int], limit: int = 50, search: str = None) -> List[Dict[str, Any]]:
        """
        Fetches users using cursor-based pagination (no OFFSET).
        """
        query = "SELECT id, email, role, created_at FROM users"
        params = []
        conditions = []

        if search:
            conditions.append("email LIKE ?")
            params.append(f"%{search}%")

        if cursor_id is not None:
            conditions.append("id < ?")
            params.append(cursor_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "email": row[1],
                "role": row[2],
                "created_at": row[3]
            })
        return users

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, email, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "email": row[1],
            "role": row[2],
            "created_at": row[3]
        }
