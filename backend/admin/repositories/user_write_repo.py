from typing import Dict, Any, Optional
import sqlite3
import time
from backend.core.db import get_conn

class UserWriteRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def update_user_role(self, user_id: int, role: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        return cursor.rowcount > 0

    def add_admin_note(self, user_id: int, admin_id: int, note: str) -> int:
        cursor = self.conn.cursor()
        now = time.time()
        cursor.execute('''
            INSERT INTO admin_notes (user_id, admin_id, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, admin_id, note, now, now))
        return cursor.lastrowid

    def add_user_tag(self, user_id: int, tag: str) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_tags (user_id, tag, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, tag, time.time()))
            return True
        except sqlite3.IntegrityError:
            return False # Tag already exists

    def remove_user_tag(self, user_id: int, tag: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM user_tags WHERE user_id = ? AND tag = ?', (user_id, tag))
        return cursor.rowcount > 0

    # Diğer write işlemleri: Delete user, vs.
