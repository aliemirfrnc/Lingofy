from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router as chat_router
from backend.routes.lyrics import router as lyrics_router
from backend.routes.translate import router as translate_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(lyrics_router)
app.include_router(translate_router)


@app.get("/health")
def health():
    return {"status": "ok"}