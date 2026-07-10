from typing import Tuple, Dict, Any
from pydantic import BaseModel

class EntityResult(BaseModel):
    """
    Represents a detected and normalized entity from speech transcription.
    """
    entity_type: str              # e.g., "PHONE_NUMBER", "OTP", "AADHAAR", "UPI_ID", "BANK_ACCOUNT"
    normalized_value: str         # The strict numeric/alphanumeric string
    raw_text: str                 # The exact spoken words matched
    speaker: str                  # Originating speaker ID
    timestamps: Tuple[float, float] # [start, end] derived from matched tokens
    language: str                 # Predominant language of the match
    confidence: float             # Final aggregated confidence score (0.0 - 1.0)
    evidence: Dict[str, Any]      # Structured audit trail of the detection
    validation_result: Dict[str, Any] # Detailed breakdown of validator checks
    context: Dict[str, Any]       # Context analyzer findings
