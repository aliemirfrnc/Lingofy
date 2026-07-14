import json
from typing import Dict, Any, Optional
from backend.core.db import get_conn
from backend.admin.repositories.user_read_repo import UserReadRepository
from backend.admin.repositories.user_write_repo import UserWriteRepository
from backend.admin.security.audit import log_admin_action
from backend.admin.events.memory_event_bus import memory_event_bus

class UserService:
    def __init__(self):
        self.read_repo = UserReadRepository()
        self.write_repo = UserWriteRepository()

    def get_users(self, cursor_id: Optional[int], limit: int = 50, search: str = None):
        return self.read_repo.get_users_paginated(cursor_id, limit, search)

    def get_user_profile(self, user_id: int):
        user = self.read_repo.get_user_by_id(user_id)
        if not user:
            return None
        # In a real scenario, this would aggregate from Subscriptions, Sessions, Learning, etc.
        return {
            "overview": user,
            "sessions": [],
            "devices": [],
            "subscriptions": []
        }

    async def update_role(self, admin_id: int, target_user_id: int, new_role: str, ip_address: Optional[str] = None):
        conn = get_conn()
        user_before = self.read_repo.get_user_by_id(target_user_id)
        if not user_before:
            raise ValueError("User not found")
            
        success = self.write_repo.update_user_role(target_user_id, new_role)
        if success:
            conn.commit()
            log_admin_action(
                admin_id=admin_id,
                action="UPDATE_USER_ROLE",
                resource="users",
                target_id=str(target_user_id),
                diff_before=json.dumps({"role": user_before["role"]}),
                diff_after=json.dumps({"role": new_role}),
                ip_address=ip_address
            )
            await memory_event_bus.publish("USER_ROLE_UPDATED", {
                "user_id": target_user_id,
                "old_role": user_before["role"],
                "new_role": new_role
            })
        else:
            conn.rollback()
        return success

    async def ban_user(self, admin_id: int, target_user_id: int, reason: str, ip_address: Optional[str] = None):
        # Implementation of ban
        conn = get_conn()
        self.write_repo.add_admin_note(target_user_id, admin_id, f"Banned: {reason}")
        # Mark sessions inactive, etc.
        conn.commit()
        
        log_admin_action(
            admin_id=admin_id,
            action="BAN_USER",
            resource="users",
            target_id=str(target_user_id),
            diff_after=json.dumps({"reason": reason}),
            ip_address=ip_address
        )
        
        await memory_event_bus.publish("USER_BANNED", {
            "user_id": target_user_id,
            "reason": reason
        })
        return True
