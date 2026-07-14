import time
from backend.core.db import get_conn
from backend.core.events import EventBus

async def create_incident(title: str, severity: str, owner: str, affected_services: str):
    conn = get_conn()
    with conn:
        cursor = conn.execute(
            """INSERT INTO incidents (title, severity, owner, affected_services, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (title, severity, owner, affected_services, time.time())
        )
        incident_id = cursor.lastrowid
        
    await EventBus.publish("INCIDENT_CREATED", {"incident_id": incident_id, "title": title, "severity": severity})
    return {"incident_id": incident_id, "status": "OPEN"}

async def resolve_incident(incident_id: int):
    conn = get_conn()
    with conn:
        conn.execute("UPDATE incidents SET status = 'RESOLVED', resolved_at = ? WHERE id = ?", (time.time(), incident_id))
    
    await EventBus.publish("INCIDENT_RESOLVED", {"incident_id": incident_id})
    return {"incident_id": incident_id, "status": "RESOLVED"}
