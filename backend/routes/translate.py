from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    translation: str


@router.post("/translate-line", response_model=TranslateResponse)
def translate_line(request: TranslateRequest):
    return {"translation": f"Çeviri: {request.text}"}
