import os
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.routes.auth import require_user_id
from backend.dependencies.subscription import enforce_usage_limit
from backend.core.providers.ai_factory import get_ai_provider

router = APIRouter()

router = APIRouter()


class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
@enforce_usage_limit(feature="ai_messages")
async def chat(
    req: ChatRequest,
    request: Request,
    authorization: str | None = Header(default=None)
):
    user_id = require_user_id(request, authorization)
    
    try:
        user_input_safe = f"<USER_INPUT>\n{req.message}\n</USER_INPUT>"
        from backend.core.services.ai_service import get_ai_service
        ai_service = get_ai_service()
        
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "chat", "system.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                sys_prompt = f.read().strip()
        else:
            sys_prompt = "Sen arkadaş canlısı bir İngilizce öğretmenisin."
            
        async def stream_generator():
            try:
                async for chunk in await ai_service.get_chat_stream(
                    system_prompt=sys_prompt,
                    messages=[{"role": "user", "content": user_input_safe}]
                ):
                    yield chunk
            except Exception as e:
                import logging
                logging.error(f"CHAT STREAM ERROR: {repr(e)}")
                yield "\nÜzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar dene."

        return StreamingResponse(stream_generator(), media_type="text/plain")
        
    except Exception as e:
        logging.error(f"CHAT ERROR: {repr(e)}")
        async def fallback_generator():
            yield "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar dene."
        return StreamingResponse(fallback_generator(), media_type="text/plain")
