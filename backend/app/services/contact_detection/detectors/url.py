from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector

class URLDetector(BaseContactDetector):
    @property
    def name(self) -> str:
        return "url"
        
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        # TODO: Implement url detection logic in future sprint
        return []
