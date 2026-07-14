import time
import json
import asyncio
from backend.core.db import get_conn
from backend.core.events import EventBus

def get_prompt_version(registry_name: str):
    conn = get_conn()
    cursor = conn.execute("SELECT current_version FROM prompt_registry WHERE name = ?", (registry_name,))
    row = cursor.fetchone()
    if not row:
        return None
    curr_ver = row[0]
    cursor = conn.execute(
        "SELECT system_prompt, variables_json FROM prompt_versions v JOIN prompt_registry r ON v.registry_id = r.id WHERE r.name = ? AND v.version = ?",
        (registry_name, curr_ver)
    )
    res = cursor.fetchone()
    if res:
        return {"version": curr_ver, "system_prompt": res[0], "variables": json.loads(res[1] or "[]")}
    return None

async def publish_prompt(registry_id: int, version: str, admin_id: int):
    conn = get_conn()
    with conn:
        conn.execute("UPDATE prompt_registry SET current_version = ?, updated_at = ? WHERE id = ?", (version, time.time(), registry_id))
    
    await EventBus.publish("PROMPT_PUBLISHED", {"registry_id": registry_id, "version": version, "admin_id": admin_id})
    return {"status": "ok", "version": version}
