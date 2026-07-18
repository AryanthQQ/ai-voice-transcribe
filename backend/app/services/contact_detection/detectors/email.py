import re
from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector
from ..i18n.manager import i18n_manager

class EmailDetector(BaseContactDetector):
    @property
    def name(self) -> str:
        return "email"
        
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        violations = []
        
        # 1. Direct Email Validation Regex (RFC 5322 approximation)
        email_pattern_str = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_pattern = i18n_manager.get_compiled_regex(self.name, "email_address", email_pattern_str, language)
        
        # 2. Intent matching
        base_keywords_list = i18n_manager.get_resource(self.name, "base_keywords", language) or ["email", "mail", "gmail", "yahoo", "outlook", "hotmail", "protonmail"]
        false_positives_list = i18n_manager.get_resource(self.name, "false_positives", language) or ["notification", "login", "password", "app", "download", "spam", "inbox", "verification", "otp", "storage", "sync", "backup", "folder"]
        intent_actions_list = i18n_manager.get_resource(self.name, "intent_actions", language) or ["id", r"contact\s+me\s+on", r"pe\s+contact\s+karna", r"bhej\s+dena", r"address\s+share\s+karo", r"send\s+to", r"email\s+karo", r"mail\s+karo"]
        
        base_keyword = r'\b(' + '|'.join(base_keywords_list) + r')\b'
        false_positives = r'(?!\s+(?:' + '|'.join(false_positives_list) + r'))'
        safe_base = rf'{base_keyword}{false_positives}'
        
        intent_actions = r'(?:' + '|'.join(intent_actions_list) + r')'
        intent_pattern_str = rf'{safe_base}(?:\s+\w+){{0,3}}\s+{intent_actions}|{intent_actions}(?:\s+\w+){{0,3}}\s+{safe_base}'
        
        intent_pattern = i18n_manager.get_compiled_regex(self.name, "intent", intent_pattern_str, language)
        
        patterns = [
            {
                "pattern": email_pattern,
                "severity": "high",
                "value": "Email Address",
                "confidence": 0.99
            },
            {
                "pattern": intent_pattern,
                "severity": "high",
                "value": "Email Request",
                "confidence": 0.99
            }
        ]

        # No standalone base keyword check as per user requirements.

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
