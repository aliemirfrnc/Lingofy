from functools import wraps
from fastapi import HTTPException, status, Depends
from backend.admin.security.authentication import get_current_admin
from backend.admin.security.permissions import has_permission, Permission
from backend.core.db import get_conn

def get_user_permissions(admin_id: int, role: str) -> list[str]:
    """
    Şimdilik Hardcoded mapping üzerinden çalışıyor.
    İleride admin_role_permissions ve admin_user_roles tablolarından okunabilir.
    """
    conn = get_conn()
    cursor = conn.cursor()
    
    # Veritabanından rol ve izinleri okuma (Future-proof implementation placeholder)
    cursor.execute('''
        SELECT p.name 
        FROM admin_user_roles ur
        JOIN admin_role_permissions rp ON ur.role_id = rp.role_id
        JOIN admin_permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = ?
    ''', (admin_id,))
    
    db_permissions = [row[0] for row in cursor.fetchall()]
    
    return list(set(db_permissions))

def requires_permission(required_permission: Permission):
    """
    Dependency decorator to check if the current admin has the required permission.
    Usage:
        @app.get("/api/admin/v1/users")
        def get_users(admin = Depends(requires_permission(Permission.USERS_READ))):
    """
    def permission_checker(admin: dict = Depends(get_current_admin)):
        user_permissions = get_user_permissions(admin["id"], admin["role"])
        
        if not has_permission(user_permissions, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yetkisiz erişim. '{required_permission.value}' izni gerekli."
            )
        return admin
        
    return permission_checker
