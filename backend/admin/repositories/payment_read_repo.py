from typing import Dict, Any, List, Optional
import sqlite3
from backend.core.db import get_conn

class PaymentReadRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def get_payments_paginated(self, cursor_id: Optional[int], limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT id, user_id, provider, amount, currency, status, created_at FROM payments"
        params = []
        
        if cursor_id is not None:
            query += " WHERE id < ?"
            params.append(cursor_id)
            
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        
        payments = []
        for row in cursor.fetchall():
            payments.append({
                "id": row[0],
                "user_id": row[1],
                "provider": row[2],
                "amount": row[3],
                "currency": row[4],
                "status": row[5],
                "created_at": row[6]
            })
        return payments
