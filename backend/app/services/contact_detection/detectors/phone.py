import re
from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector
from ..i18n.manager import i18n_manager

class PhoneDetector(BaseContactDetector):
    @property
    def name(self) -> str:
        return "phone_number"
        
    def _normalize_spoken_numbers(self, text: str, language: Optional[str] = None) -> str:
        """
        Convert spoken number words into digits in the text based on the i18n resources.
        Handles basic sequences like 'nine eight seven' -> '987'.
        """
        number_words = i18n_manager.get_resource("phone", "number_words", language)
        if not number_words:
            # Default empty map if no resources loaded
            number_words = {}
            
        words = text.lower().split()
        normalized = []
        
        i = 0
        while i < len(words):
            word = re.sub(r'[^a-z]', '', words[i])
            if word in number_words:
                val = number_words[word]
                if val.startswith("x"):
                    multiplier = int(val[1:])
                    # duplicate the next number if it is a number word
                    if i + 1 < len(words):
                        next_word = re.sub(r'[^a-z]', '', words[i+1])
                        if next_word in number_words and not number_words[next_word].startswith("x"):
                            normalized.append(number_words[next_word] * multiplier)
                            i += 1 # skip next word
                        else:
                            normalized.append(word)
                else:
                    normalized.append(val)
            else:
                normalized.append(words[i])
            i += 1
            
        return " ".join(normalized)
        
    def detect(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        # Regex to capture phone numbers:
        phone_regex = r'(?:(?:\+91|91)[\s-]*)?(?:\d[\s-]*){10}'
        
        violations = []
        
        if segments:
            for segment in segments:
                text = segment.get("text", "")
                norm_text = self._normalize_spoken_numbers(text, language)
                
                for match in re.finditer(phone_regex, norm_text):
                    raw_match = match.group(0)
                    digits_only = re.sub(r'\D', '', raw_match)
                    
                    if len(digits_only) == 10 or (len(digits_only) == 12 and digits_only.startswith("91")):
                        start_time = segment.get("start", 0.0)
                        minutes = int(start_time // 60)
                        seconds = int(start_time % 60)
                        time_str = f"{minutes:02d}:{seconds:02d}"
                        
                        violations.append({
                            "type": self.name,
                            "severity": "High",
                            "value": digits_only[-10:],
                            "timestamp": time_str,
                            "speaker": segment.get("speaker", "Unknown"),
                            "confidence": 0.99,
                            "matched_text": raw_match
                        })
        else:
            norm_text = self._normalize_spoken_numbers(transcript, language)
            for match in re.finditer(phone_regex, norm_text):
                raw_match = match.group(0)
                digits_only = re.sub(r'\D', '', raw_match)
                if len(digits_only) == 10 or (len(digits_only) == 12 and digits_only.startswith("91")):
                    violations.append({
                        "type": self.name,
                        "severity": "High",
                        "value": digits_only[-10:],
                        "timestamp": "00:00",
                        "speaker": "Unknown",
                        "confidence": 0.99,
                        "matched_text": raw_match
                    })
                    
        return violations
