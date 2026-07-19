import re
from typing import List, Dict, Optional, Any
from ..base import BaseContactDetector
from ..i18n.manager import i18n_manager
from app.core.logger import logger

DEBUG_PHONE_DETECTOR = True

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
        print("\n######## PHONE DETECTOR CALLED ########")
        # Regex to capture phone numbers:
        phone_regex = r'(?:(?:\+91|91)[\s-]*)?(?:\d[\s-]*){10}'
        
        violations = []
        
        if segments:
            for segment in segments:
                text = segment.get("text", "")
                print(f"\nSEGMENT TEXT:\n{text}")
                
                norm_text = self._normalize_spoken_numbers(text, language)
                print(f"\nNORMALIZED:\n{norm_text}")
                
                print("Searching regex...")
                for match in re.finditer(phone_regex, norm_text):
                    raw_match = match.group(0)
                    digits_only = re.sub(r'\D', '', raw_match)
                    
                    print(f"RAW MATCH: {raw_match}")
                    print(f"DIGITS: {digits_only}")
                    
                    if len(digits_only) == 10 or (len(digits_only) == 12 and digits_only.startswith("91")):
                        print("PHONE VIOLATION CREATED")
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
                        print("PHONE VIOLATION SKIPPED")
                        
            # Second pass: Sliding window (2 and 3 segments)
            found_numbers = {v["value"] for v in violations}
            norm_segments = [self._normalize_spoken_numbers(seg.get("text", ""), language) for seg in segments]
            
            for window_size in [2, 3]:
                for i in range(len(norm_segments) - window_size + 1):
                    window_text = " ".join(norm_segments[i:i + window_size])
                    
                    # Reconstruct consecutive digits across segments
                    window_text = re.sub(r'(?<=\d)[\s-]+(?=\d)', '', window_text)
                    
                    for match in re.finditer(phone_regex, window_text):
                        raw_match = match.group(0)
                        digits_only = re.sub(r'\D', '', raw_match)
                        
                        if len(digits_only) == 10 or (len(digits_only) == 12 and digits_only.startswith("91")):
                            value = digits_only[-10:]
                            if value not in found_numbers:
                                found_numbers.add(value)
                                start_time = segments[i].get("start", 0.0)
                                minutes = int(start_time // 60)
                                seconds = int(start_time % 60)
                                time_str = f"{minutes:02d}:{seconds:02d}"
                                
                                violations.append({
                                    "type": self.name,
                                    "severity": "High",
                                    "value": value,
                                    "timestamp": time_str,
                                    "speaker": segments[i].get("speaker", "Unknown"),
                                    "confidence": 0.99,
                                    "matched_text": raw_match
                                })
        else:
            norm_text = self._normalize_spoken_numbers(transcript, language)
            
            print(f"\nNORMALIZED:\n{norm_text}")
            print("Searching regex...")
            for match in re.finditer(phone_regex, norm_text):
                raw_match = match.group(0)
                digits_only = re.sub(r'\D', '', raw_match)
                
                print(f"RAW MATCH: {raw_match}")
                print(f"DIGITS: {digits_only}")
                
                if len(digits_only) == 10 or (len(digits_only) == 12 and digits_only.startswith("91")):
                    print("PHONE VIOLATION CREATED")
                    violations.append({
                        "type": self.name,
                        "severity": "High",
                        "value": digits_only[-10:],
                        "timestamp": "00:00",
                        "speaker": "Unknown",
                        "confidence": 0.99,
                        "matched_text": raw_match
                    })
                else:
                    print("PHONE VIOLATION SKIPPED")
                    
        print(f"TOTAL PHONE VIOLATIONS: {len(violations)}")
        return violations
