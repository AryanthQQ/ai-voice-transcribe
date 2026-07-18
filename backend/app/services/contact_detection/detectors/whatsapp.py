import re
from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector
from ..i18n.manager import i18n_manager

class WhatsAppDetector(BaseContactDetector):
    @property
    def name(self) -> str:
        return "whatsapp"
        
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        violations = []
        
        base_keywords_list = i18n_manager.get_resource(self.name, "base_keywords", language)
        intent_actions_list = i18n_manager.get_resource(self.name, "intent_actions", language)
        
        if not base_keywords_list:
            base_keywords_list = ["whatsapp", "wa", "wp"]
        if not intent_actions_list:
            intent_actions_list = ["number", "message", "share"]
            
        base_keyword = r'\b(?:' + '|'.join(base_keywords_list) + r')\b'
        intent_actions = r'(?:' + '|'.join(intent_actions_list) + r')'
        
        intent_pattern_str = rf'{base_keyword}(?:\s+\w+){{0,3}}\s+{intent_actions}'
        
        # Use compiled regex cache
        intent_pattern = i18n_manager.get_compiled_regex(self.name, "intent", intent_pattern_str, language)
        base_pattern = i18n_manager.get_compiled_regex(self.name, "base", base_keyword, language)
        
        patterns = [
            {
                "pattern": intent_pattern,
                "severity": "High",
                "value": "WhatsApp Request",
                "confidence": 0.99
            }
        ]

        if segments:
            for segment in segments:
                text = segment.get("text", "")
                existing = []
                segment_violations = self._extract_violations(text, patterns, segment, existing)
                
                # Check for standalone keywords
                for match in base_pattern.finditer(text):
                    span = match.span()
                    is_overlap = any(i_span[0] <= span[0] and span[1] <= i_span[1] for i_span in existing)
                    if not is_overlap:
                        start_time = segment.get("start", 0.0)
                        minutes = int(start_time // 60)
                        seconds = int(start_time % 60)
                        time_str = f"{minutes:02d}:{seconds:02d}"
                        segment_violations.append({
                            "type": self.name,
                            "severity": "Medium",
                            "value": "WhatsApp Keyword",
                            "timestamp": time_str,
                            "speaker": segment.get("speaker", "Unknown"),
                            "confidence": 0.70,
                            "matched_text": match.group(0)
                        })
                
                violations.extend(segment_violations)
        else:
            text = transcript
            existing = []
            transcript_violations = self._extract_violations(text, patterns, None, existing)
            
            for match in base_pattern.finditer(text):
                span = match.span()
                is_overlap = any(i_span[0] <= span[0] and span[1] <= i_span[1] for i_span in existing)
                if not is_overlap:
                    transcript_violations.append({
                        "type": self.name,
                        "severity": "Medium",
                        "value": "WhatsApp Keyword",
                        "timestamp": "00:00",
                        "speaker": "Unknown",
                        "confidence": 0.70,
                        "matched_text": match.group(0)
                    })
                    
            violations.extend(transcript_violations)
                    
        return violations
