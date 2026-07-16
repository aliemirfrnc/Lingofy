"""
ProfileService — application-level business logic for /api/me endpoints.

Responsibilities:
  - Input validation (domain rules, not HTTP)
  - Orchestration of repository calls
  - No SQL; no HTTP concerns
"""
from typing import Any, Dict, List, Optional

from backend.core.repositories.profile_repo import ProfileRepo
from backend.core.logger import get_logger

logger = get_logger("lingofy.services.profile")

_repo = ProfileRepo()

# Supported languages catalogue (ISO 639-1 codes + English label)
SUPPORTED_LANGUAGES: List[Dict[str, str]] = [
    {"code": "en", "name": "English"},
    {"code": "tr", "name": "Turkish"},
    {"code": "de", "name": "German"},
    {"code": "fr", "name": "French"},
    {"code": "es", "name": "Spanish"},
    {"code": "it", "name": "Italian"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ar", "name": "Arabic"},
    {"code": "nl", "name": "Dutch"},
    {"code": "pl", "name": "Polish"},
    {"code": "sv", "name": "Swedish"},
]

VALID_THEMES = {"light", "dark", "system"}
VALID_LANGUAGE_CODES = {lang["code"] for lang in SUPPORTED_LANGUAGES}
MAX_DISPLAY_NAME_LENGTH = 50
MIN_DAILY_GOAL_MINUTES = 5
MAX_DAILY_GOAL_MINUTES = 240


class ProfileService:
    @staticmethod
    def get_profile(user_id: int) -> Dict[str, Any]:
        """Return full profile data for a user."""
        user = _repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        import datetime
        created = user["created_at"]
        created_iso = (
            datetime.datetime.utcfromtimestamp(created).isoformat() + "Z"
            if isinstance(created, (int, float))
            else str(created)
        )
        return {
            "id": user["id"],
            "email": user["email"],
            "display_name": user.get("display_name") or "",
            "role": user.get("role", "USER"),
            "created_at": created_iso,
        }

    @staticmethod
    def update_profile(user_id: int, display_name: str) -> Dict[str, Any]:
        """Update the user's display name; return updated profile."""
        display_name = display_name.strip()
        if not display_name:
            raise ValueError("display_name cannot be empty")
        if len(display_name) > MAX_DISPLAY_NAME_LENGTH:
            raise ValueError(
                f"display_name must be at most {MAX_DISPLAY_NAME_LENGTH} characters"
            )
        _repo.update_display_name(user_id, display_name)
        logger.info(f"Profile updated user_id={user_id} field=display_name")
        return ProfileService.get_profile(user_id)

    @staticmethod
    def get_preferences(user_id: int) -> Dict[str, Any]:
        return _repo.get_preferences(user_id)

    @staticmethod
    def update_preferences(user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and apply preference updates; return the full updated preferences."""
        validated: Dict[str, Any] = {}

        if "theme" in updates:
            theme = updates["theme"]
            if theme not in VALID_THEMES:
                raise ValueError(f"theme must be one of {sorted(VALID_THEMES)}")
            validated["theme"] = theme

        for lang_field in ("interface_language", "target_language"):
            if lang_field in updates:
                code = updates[lang_field]
                if code not in VALID_LANGUAGE_CODES:
                    raise ValueError(
                        f"{lang_field} must be a valid language code"
                    )
                validated[lang_field] = code

        if "daily_goal_minutes" in updates:
            goal = updates["daily_goal_minutes"]
            if not isinstance(goal, int) or not (
                MIN_DAILY_GOAL_MINUTES <= goal <= MAX_DAILY_GOAL_MINUTES
            ):
                raise ValueError(
                    f"daily_goal_minutes must be between "
                    f"{MIN_DAILY_GOAL_MINUTES} and {MAX_DAILY_GOAL_MINUTES}"
                )
            validated["daily_goal_minutes"] = goal

        if "timezone" in updates:
            validated["timezone"] = str(updates["timezone"])[:64]

        for bool_field in ("email_notifications", "push_notifications", "marketing_emails"):
            if bool_field in updates:
                val = updates[bool_field]
                if not isinstance(val, bool):
                    raise ValueError(f"{bool_field} must be a boolean")
                validated[bool_field] = val

        _repo.update_preferences(user_id, validated)
        logger.info(f"Preferences updated user_id={user_id} fields={list(validated)}")
        return ProfileService.get_preferences(user_id)

    @staticmethod
    def list_sessions(user_id: int) -> List[Dict[str, Any]]:
        return _repo.list_sessions(user_id)

    @staticmethod
    def revoke_session(user_id: int, session_id: str) -> bool:
        """Revoke a single session. Returns False if session was not found."""
        revoked = _repo.revoke_session(user_id, session_id)
        if revoked:
            logger.info(f"Session revoked user_id={user_id} session_id={session_id}")
        return revoked

    @staticmethod
    def revoke_other_sessions(user_id: int, current_token_hash: Optional[str]) -> int:
        """Revoke all sessions except the current one."""
        if not current_token_hash:
            return 0
        count = _repo.revoke_other_sessions(user_id, current_token_hash)
        logger.info(f"Other sessions revoked user_id={user_id} count={count}")
        return count

    @staticmethod
    def list_languages() -> List[Dict[str, str]]:
        """Return all supported language codes and names."""
        return SUPPORTED_LANGUAGES
