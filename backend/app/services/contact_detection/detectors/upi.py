from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector

class UPIDetector(BaseContactDetector):
    @property
    def name(self) -> str:
        return "upi"
        
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        # TODO: Implement upi detection logic in future sprint
        return []
