from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Turn(BaseModel):
    speaker: str
    text: str
    time: str
    english: Optional[str] = None

class Incident(BaseModel):
    time: str
    speaker: str
    text: str
    violations: List[str]

class AnalyzeCallResponse(BaseModel):
    success: bool
    transcript: str
    turns: List[Turn]
    language: str
    summary: Optional[str] = None
    incidents: Optional[List[Incident]] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
