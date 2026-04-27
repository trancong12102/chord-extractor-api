from pydantic import BaseModel, HttpUrl


class ExtractRequest(BaseModel):
    url: HttpUrl


class Chord(BaseModel):
    chord: str
    timestamp: float


class ExtractResponse(BaseModel):
    duration: float
    chords: list[Chord]
