"""
/api/me — Profile, Preferences, Sessions, Languages

All routes:
  - Require authentication via existing require_user_id dependency
  - Contain NO SQL, NO business logic
  - Delegate to ProfileService
  - Return RFC7807-compatible errors via existing global handlers

OpenAPI endpoints:
  GET    /api/me                       → full user profile
  PATCH  /api/me                       → update display_name
  GET    /api/me/preferences           → user preferences
  PATCH  /api/me/preferences           → update preferences
  GET    /api/me/sessions              → list active sessions
  DELETE /api/me/sessions/{session_id} → revoke a session
  DELETE /api/me/sessions/others       → revoke all sessions except current
  GET    /api/me/languages             → supported language list (static)
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from backend.core.services.profile_service import ProfileService
from backend.routes.auth import require_user_id
from backend.core.logger import get_logger

logger = get_logger("lingofy.routes.me")

router = APIRouter(prefix="/api/me", tags=["profile"])


# ---------------------------------------------------------------------------
# Request DTOs
# ---------------------------------------------------------------------------

class UpdateProfileRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)


class UpdatePreferencesRequest(BaseModel):
    theme: Optional[str] = Field(None, description="light | dark | system")
    interface_language: Optional[str] = Field(None, description="ISO 639-1 language code")
    target_language: Optional[str] = Field(None, description="ISO 639-1 language code")
    daily_goal_minutes: Optional[int] = Field(None, ge=5, le=240)
    timezone: Optional[str] = Field(None, max_length=64)
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None


# ---------------------------------------------------------------------------
# GET /api/me
# ---------------------------------------------------------------------------

@router.get(
    "",
    summary="Get current user profile",
    response_description="Full profile including email, display_name, role, created_at.",
)
def get_profile(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Return the full profile of the currently authenticated user."""
    user_id = require_user_id(request, authorization)
    return ProfileService.get_profile(user_id)


# ---------------------------------------------------------------------------
# PATCH /api/me
# ---------------------------------------------------------------------------

@router.patch(
    "",
    summary="Update user profile",
    response_description="Updated profile.",
)
def update_profile(
    body: UpdateProfileRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Update the authenticated user's display name."""
    user_id = require_user_id(request, authorization)
    try:
        return ProfileService.update_profile(user_id, body.display_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /api/me/preferences
# ---------------------------------------------------------------------------

@router.get(
    "/preferences",
    summary="Get user preferences",
    response_description="Theme, languages, daily goal, notifications.",
)
def get_preferences(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Return the authenticated user's preferences."""
    user_id = require_user_id(request, authorization)
    return ProfileService.get_preferences(user_id)


# ---------------------------------------------------------------------------
# PATCH /api/me/preferences
# ---------------------------------------------------------------------------

@router.patch(
    "/preferences",
    summary="Update user preferences",
    response_description="Updated preferences.",
)
def update_preferences(
    body: UpdatePreferencesRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Partially update the authenticated user's preferences."""
    user_id = require_user_id(request, authorization)
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    try:
        return ProfileService.update_preferences(user_id, updates)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /api/me/sessions
# ---------------------------------------------------------------------------

@router.get(
    "/sessions",
    summary="List active sessions",
    response_description="List of active refresh-token sessions.",
)
def list_sessions(
    request: Request,
    authorization: str | None = Header(default=None),
) -> List[Dict[str, Any]]:
    """Return all currently active sessions for the authenticated user."""
    user_id = require_user_id(request, authorization)
    return ProfileService.list_sessions(user_id)


# ---------------------------------------------------------------------------
# DELETE /api/me/sessions/others — MUST be defined before /{session_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/sessions/others",
    summary="Revoke all other sessions",
    response_description="Number of sessions revoked.",
)
def revoke_other_sessions(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """
    Revoke all active sessions except the current one.

    The current session is identified via the `refresh_token` cookie.
    If no refresh token is present the endpoint still succeeds (idempotent).
    """
    user_id = require_user_id(request, authorization)
    from backend.core.auth import decode_access_token

    # Identify the current session's refresh_token hash from cookie
    refresh_token = request.cookies.get("refresh_token")
    current_hash: Optional[str] = None
    if refresh_token:
        from hashlib import sha256
        current_hash = sha256(refresh_token.encode()).hexdigest()

    count = ProfileService.revoke_other_sessions(user_id, current_hash)
    return {"revoked": count, "status": "ok"}


# ---------------------------------------------------------------------------
# DELETE /api/me/sessions/{session_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/sessions/{session_id}",
    summary="Revoke a specific session",
    response_description="Revocation status.",
)
def revoke_session(
    session_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    """Revoke a specific active session identified by its session_id."""
    user_id = require_user_id(request, authorization)
    revoked = ProfileService.revoke_session(user_id, session_id)
    if not revoked:
        raise HTTPException(
            status_code=404,
            detail="Session not found or already expired.",
        )
    return {"session_id": session_id, "status": "revoked"}


# ---------------------------------------------------------------------------
# GET /api/me/languages
# ---------------------------------------------------------------------------

@router.get(
    "/languages",
    summary="Supported languages",
    response_description="List of ISO 639-1 language codes supported by the platform.",
)
def list_languages() -> List[Dict[str, str]]:
    """Return the static list of language codes supported by the platform."""
    return ProfileService.list_languages()
