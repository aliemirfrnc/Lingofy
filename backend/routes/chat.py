from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

FREE_DAILY_LIMIT = 5
message_count = 0
counter_date = date.today()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    global message_count, counter_date

    today = date.today()
    if counter_date != today:
        counter_date = today
        message_count = 0

    if message_count >= FREE_DAILY_LIMIT:
        raise HTTPException(status_code=429, detail="Daily message limit reached")

    message_count += 1
    return {"response": f"Mesajınız alındı: {request.message}"}
