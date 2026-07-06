from pydantic import BaseModel, HttpUrl
from typing import Optional

class AnalyzeCallRequest(BaseModel):
    user_id: str
    adviser_id: str
    voice_url: HttpUrl

class TranscribeRequest(BaseModel):
    language: Optional[str] = "auto"
    prompt: Optional[str] = "हाँ, ठीक है, जी, अच्छा।"
    translate: bool = True
