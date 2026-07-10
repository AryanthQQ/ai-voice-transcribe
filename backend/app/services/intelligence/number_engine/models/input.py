from typing import Optional
from pydantic import BaseModel

class TranscriptSegment(BaseModel):
    """
    Represents a single continuous segment of transcribed speech.
    """
    text: str
    start: float
    end: float
    speaker: str
    confidence: float
    detected_language: Optional[str] = None
