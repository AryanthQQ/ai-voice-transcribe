from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import re

class BaseContactDetector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
        
    def _extract_violations(self, text: str, patterns: List[Dict[str, Any]], 
                            segment: Optional[Dict[str, Any]] = None, 
                            existing_matches: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """
        Helper method to extract violations based on regex patterns.
        patterns should be a list of dicts: {"pattern": re.Pattern, "severity": "high", "value": "Desc", "confidence": 0.99}
        existing_matches is an optional list of (start, end) spans to avoid overlapping detections.
        Returns a list of violation dicts.
        """
        violations = []
        if existing_matches is None:
            existing_matches = []
            
        for config in patterns:
            pattern = config["pattern"]
            for match in pattern.finditer(text):
                span = match.span()
                # Check for overlap
                is_overlap = any(i_span[0] <= span[0] and span[1] <= i_span[1] for i_span in existing_matches)
                if not is_overlap:
                    start_time = segment.get("start", 0.0) if segment else 0.0
                    minutes = int(start_time // 60)
                    seconds = int(start_time % 60)
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    
                    violations.append({
                        "type": self.name,
                        "severity": config["severity"],
                        "value": config["value"],
                        "timestamp": time_str if segment else "00:00",
                        "speaker": segment.get("speaker", "Unknown") if segment else "Unknown",
                        "confidence": config["confidence"],
                        "matched_text": match.group(0)
                    })
                    existing_matches.append(span)
                    
        return violations
