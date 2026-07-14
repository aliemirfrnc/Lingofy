import time
import asyncio
from backend.core.db import get_conn
from backend.core.events import EventBus
from backend.core.services.ai_service import get_ai_service

async def replay_conversation(conversation_id: int, admin_id: int, provider: str = None, model: str = None):
    conn = get_conn()
    cursor = conn.execute("SELECT user_prompt, system_prompt FROM ai_conversations WHERE id = ?", (conversation_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError("Conversation not found")
        
    user_prompt, system_prompt = row
    
    await EventBus.publish("AI_REPLAY_STARTED", {"conversation_id": conversation_id, "admin_id": admin_id})
    
    start_time = time.time()
    
    # Simulate replay processing
    await asyncio.sleep(0.1)
    response = f"[REPLAY] Mocked response for: {user_prompt}"
    latency = time.time() - start_time
    cost = 0.0001
    
    with conn:
        conn.execute(
            """INSERT INTO ai_replays (conversation_id, admin_id, provider, model, prompt, response, latency, cost, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (conversation_id, admin_id, provider or "mock_provider", model or "mock_model", user_prompt, response, latency, cost, time.time())
        )
    
    await EventBus.publish("AI_REPLAY_FINISHED", {"conversation_id": conversation_id, "admin_id": admin_id, "latency": latency})
    return {"status": "ok", "response": response, "latency": latency}
