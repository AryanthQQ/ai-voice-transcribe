from typing import Optional, List, Tuple
from pydantic import BaseModel

class IntentInput(BaseModel):
    """
    Represents a single continuous segment of transcribed speech.
    """
    text: str
    start: float
    end: float
    speaker: str
    confidence: float
    detected_language: Optional[str] = None

class IntentResult(BaseModel):
    """
    Represents a detected contact intent from speech transcription.
    """
    intent: str                   # e.g., "CONTACT_SHARE"
    channel: str                  # e.g., "WHATSAPP", "PHONE", "INSTAGRAM"
    action: str                   # e.g., "ADD", "CALL", "MESSAGE", "PAY"
    matched_text: str             # The exact spoken words matched
    confidence: float             # Final aggregated confidence score (0.0 - 1.0)
    speaker: str                  # Originating speaker ID
    timestamps: Tuple[float, float] # [start, end] derived from matched tokens
