from fastapi import APIRouter, Header, HTTPException, Response, Request
from pydantic import BaseModel

from backend.core.auth import (
    create_token_pair,
    create_user,
    decode_access_token,
    get_user_by_email,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_password,
)
from backend.core.db import get_conn, get_lock
from backend.core.services.auth_service import (
    record_failed_attempt, reset_attempts, is_locked_out, logout_all_devices
)
import re

router = APIRouter(prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    status: str
    email: str
    message: str = ""

class MeResponse(BaseModel):
    email: str

def _set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    # SameSite=Lax allows frontend and backend to communicate if on same localhost domain
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=900)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=2592000)

def _clear_auth_cookies(response: Response):
    response.delete_cookie(key="access_token", httponly=True, secure=False, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, secure=False, samesite="lax")

def _extract_token(request: Request, authorization: str | None) -> str:
    # First try cookie
    token = request.cookies.get("access_token")
    if token:
        return token
    # Fallback to header
    if authorization and authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    raise HTTPException(status_code=401, detail="Giriş yapman gerekiyor.")

def require_user_id(request: Request, authorization: str | None = Header(default=None)) -> int:
    token = _extract_token(request, authorization)
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Oturum süresi dolmuş, tekrar giriş yap.")
    return user_id

@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, response: Response):
    email = payload.email.strip().lower()

    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Geçerli bir e-posta adresi gir.")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Şifre en az 8 karakter olmalı.")
    if get_user_by_email(email):
        raise HTTPException(status_code=409, detail="Bu e-posta zaten kayıtlı.")

    user_id = create_user(email, payload.password)
    access_token, refresh_token = create_token_pair(user_id, email)
    _set_auth_cookies(response, access_token, refresh_token)
    return {"status": "ok", "email": email, "message": "Kayıt başarılı."}

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, response: Response):
    ip = request.client.host if request.client else "unknown"
    email = payload.email.strip().lower()
    
    if is_locked_out(ip, email):
        raise HTTPException(status_code=429, detail="Çok fazla hatalı deneme yaptın. Lütfen 15 dakika bekle.")
        
    row = get_user_by_email(email)
    if not row or not verify_password(payload.password, row[2]):
        record_failed_attempt(ip, email)
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı.")

    reset_attempts(ip, email)
    access_token, refresh_token = create_token_pair(row[0], email)
    _set_auth_cookies(response, access_token, refresh_token)
    return {"status": "ok", "email": email, "message": "Giriş başarılı."}

@router.post("/refresh", response_model=AuthResponse)
def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        # Fallback to checking body if needed, but we rely on cookie
        raise HTTPException(status_code=401, detail="Oturum süresi dolmuş, tekrar giriş yap.")
        
    result = rotate_refresh_token(refresh_token)
    if not result:
        _clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Oturum süresi dolmuş, tekrar giriş yap.")
        
    access_token, new_refresh, email = result
    _set_auth_cookies(response, access_token, new_refresh)
    return {"status": "ok", "email": email, "message": "Token yenilendi."}

@router.get("/me", response_model=MeResponse)
def me(request: Request, authorization: str | None = Header(default=None)):
    user_id = require_user_id(request, authorization)
    conn = get_conn()
    with get_lock():
        cur = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı.")
    return {"email": row[0]}

@router.post("/logout")
def logout(request: Request, response: Response, authorization: str | None = Header(default=None)):
    try:
        require_user_id(request, authorization)
    except:
        pass
    
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        revoke_refresh_token(refresh_token)
        
    _clear_auth_cookies(response)
    return {"status": "ok"}

@router.post("/logout-all")
def logout_all(request: Request, response: Response, authorization: str | None = Header(default=None)):
    user_id = require_user_id(request, authorization)
    logout_all_devices(user_id)
    _clear_auth_cookies(response)
    return {"status": "ok"}
