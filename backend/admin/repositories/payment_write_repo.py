from typing import Dict, Any, Optional
import sqlite3
import time
from backend.core.db import get_conn

class PaymentWriteRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def create_payment(self, user_id: int, provider: str, amount: float, currency: str, status: str, invoice_id: Optional[str] = None, transaction_id: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, provider, amount, currency, status, invoice_id, transaction_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, provider, amount, currency, status, invoice_id, transaction_id, time.time()))
        return cursor.lastrowid

    def update_payment_status(self, payment_id: int, status: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
        return cursor.rowcount > 0

    def add_payment_event(self, payment_id: int, event_type: str, provider_event_id: Optional[str], payload_json: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payment_events (payment_id, event_type, provider_event_id, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (payment_id, event_type, provider_event_id, payload_json, time.time()))
        return cursor.lastrowid
