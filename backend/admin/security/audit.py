import time
from typing import Optional
from fastapi import Request
from backend.core.db import get_conn
from backend.core.logger import request_id_ctx, correlation_id_ctx

def log_admin_action(
    admin_id: int,
    action: str,
    resource: str,
    target_id: Optional[str] = None,
    diff_before: Optional[str] = None,
    diff_after: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """
    Logs an action performed by an admin.
    """
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO admin_audit_logs 
            (admin_id, action, resource, target_id, diff_before, diff_after, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, action, resource, target_id, diff_before, diff_after, ip_address, time.time()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        # Non-blocking error handling for audit failures
        import logging
        logging.error(f"Failed to write admin audit log: {e}")

def get_audit_info(request: Request):
    """
    Extracts IP address and context IDs.
    """
    return {
        "ip_address": request.client.host if request.client else None,
        "request_id": request_id_ctx.get(),
        "correlation_id": correlation_id_ctx.get()
    }
