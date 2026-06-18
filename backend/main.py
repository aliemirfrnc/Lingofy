from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.chat import router as chat_router
from routes.lyrics import router as lyrics_router
from routes.translate import router as translate_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(chat_router)
app.include_router(lyrics_router)
app.include_router(translate_router)


@app.get("/health")
def health():
    return {"status": "ok"}
