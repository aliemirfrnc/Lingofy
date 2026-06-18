from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LyricsResponse(BaseModel):
    lyrics: list[str]


MOCK_LYRICS = {
    "default": [
        "First line of the song",
        "Second line of the song",
        "Third line of the song",
    ]
}


@router.get("/lyrics", response_model=LyricsResponse)
def get_lyrics(song: str):
    return {"lyrics": MOCK_LYRICS.get(song.lower(), MOCK_LYRICS["default"])}
