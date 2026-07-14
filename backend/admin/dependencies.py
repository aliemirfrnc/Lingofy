from fastapi import Request, HTTPException, Depends
from backend.routes.auth import require_user_id
from backend.core.db import get_conn
import json
import time

def get_admin_id(request: Request, user_id: int = Depends(require_user_id)) -> int:
    conn = get_conn()
    cursor = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row or row[0] not in ["SUPER_ADMIN", "ADMIN", "SUPPORT", "FINANCE", "AI_ENGINEER"]:
        raise HTTPException(status_code=403, detail="Erişim engellendi. Bu işlem için Admin yetkisi gerekiyor.")
    request.state.admin_role = row[0]
    return user_id

def require_role(allowed_roles: list):
    def role_checker(request: Request, admin_id: int = Depends(get_admin_id)):
        role = getattr(request.state, "admin_role", None)
        if role not in allowed_roles and role != "SUPER_ADMIN":
            raise HTTPException(status_code=403, detail=f"Erişim engellendi. Gerekli roller: {allowed_roles}")
        return admin_id
    return role_checker

def audit_log(admin_id: int, action: str, resource: str, target_id: str = None, diff_before: dict = None, diff_after: dict = None, ip_address: str = None):
    conn = get_conn()
    with conn:
        conn.execute(
            """
            INSERT INTO admin_audit_logs (admin_id, action, resource, target_id, diff_before, diff_after, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                admin_id, action, resource, target_id, 
                json.dumps(diff_before) if diff_before else None, 
                json.dumps(diff_after) if diff_after else None, 
                ip_address, time.time()
            )
        )
