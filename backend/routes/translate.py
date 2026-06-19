from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deep_translator import GoogleTranslator

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    translation: str


@router.post("/translate-line", response_model=TranslateResponse)
def translate_line(request: TranslateRequest):
    try:
        result = GoogleTranslator(source="auto", target="tr").translate(request.text)
        return {"translation": result}
    except Exception:
        raise HTTPException(status_code=500, detail="Çeviri başarısız.")