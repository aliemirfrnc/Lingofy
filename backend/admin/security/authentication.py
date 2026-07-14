from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from backend.core.auth import decode_access_token
from backend.core.db import get_conn
import sqlite3

security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    user_dict = {
        "id": user[0],
        "email": user[1],
        "role": user[2]
    }
    
    # Sadece admin rollerine sahip olanlar geçebilir
    # Eğer rol tablosunda role yoksa ama user.role içerisinde admin yetkisi varsa kabul et
    if user_dict["role"] == "USER":
        raise HTTPException(status_code=403, detail="Admin yetkisi gereklidir.")

    return user_dict
