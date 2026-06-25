import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel

from backend.routes.auth import require_user_id
from backend.dependencies.subscription import enforce_usage_limit
from backend.core.providers.ai_factory import get_ai_provider

router = APIRouter()

with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "chat_system.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
@enforce_usage_limit(feature="ai_messages")
async def chat(
    req: ChatRequest,
    request: Request,
    authorization: str | None = Header(default=None)
):
    user_id = require_user_id(request, authorization)
    
    try:
        user_input_safe = f"<USER_INPUT>\n{req.message}\n</USER_INPUT>"
        
        provider = get_ai_provider()
        response_text = await provider.generate_text(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_input_safe,
            temperature=0.4
        )
        return {"response": response_text}
    except Exception as e:
        print("CHAT ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="AI yanıt veremedi.")
