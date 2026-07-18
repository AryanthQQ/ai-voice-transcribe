import re
from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector
from ..i18n.manager import i18n_manager

class TelegramDetector(BaseContactDetector):
    @property
    def name(self) -> str:
        return "telegram"
        
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        violations = []
        
        base_keywords_list = i18n_manager.get_resource(self.name, "base_keywords", language) or ["telegram", "tg"]
        false_positives_list = i18n_manager.get_resource(self.name, "false_positives", language) or ["app", "download", "update", "login", "settings", "notification", "premium", r"channel\s+news"]
        intent_actions_list = i18n_manager.get_resource(self.name, "intent_actions", language) or ["id", "username", r"pe\s+aa\s+jana", r"pe\s+message\s+karna", r"share\s+karo", r"de\s+do"]
        link_patterns_list = i18n_manager.get_resource(self.name, "link_patterns", language) or [r"(?:https?://)?(?:t\.me|telegram\.me)/[\w.-]+"]
        
        base_keyword = r'\b(' + '|'.join(base_keywords_list) + r')\b'
        false_positives = r'(?!\s+(?:' + '|'.join(false_positives_list) + r'))'
        safe_base = rf'{base_keyword}{false_positives}'
        
        intent_actions = r'(?:' + '|'.join(intent_actions_list) + r')'
        intent_pattern_str = rf'{safe_base}(?:\s+\w+){{0,3}}\s+{intent_actions}'
        
        link_pattern_str = r'\b(' + '|'.join(link_patterns_list) + r')\b'
        
        intent_pattern = i18n_manager.get_compiled_regex(self.name, "intent", intent_pattern_str, language)
        link_pattern = i18n_manager.get_compiled_regex(self.name, "link", link_pattern_str, language)
        base_pattern = i18n_manager.get_compiled_regex(self.name, "base", safe_base, language)
        
        patterns = [
            {
                "pattern": link_pattern,
                "severity": "high",
                "value": "Telegram Link",
                "confidence": 0.99
            },
            {
                "pattern": intent_pattern,
                "severity": "high",
                "value": "Telegram Request",
                "confidence": 0.99
            }
        ]

        if segments:
            for segment in segments:
                text = segment.get("text", "")
                existing = []
                segment_violations = self._extract_violations(text, patterns, segment, existing)
                
                violations.extend(segment_violations)
        else:
            text = transcript
            existing = []
            transcript_violations = self._extract_violations(text, patterns, None, existing)
            violations.extend(transcript_violations)
            
        return violations
