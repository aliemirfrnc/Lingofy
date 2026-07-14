from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.auth import decode_access_token
from backend.core.db import get_conn, get_lock

security = HTTPBearer(auto_error=False)

def get_current_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Resolve the canonical integer user id from the same JWT contract as user routes."""
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    user_id = decode_access_token(token) if token else None
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})

    with get_lock():
        user = get_conn().execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user[2] == "USER":
        raise HTTPException(status_code=403, detail="Admin permission is required")
    return {"id": user[0], "email": user[1], "role": user[2]}
