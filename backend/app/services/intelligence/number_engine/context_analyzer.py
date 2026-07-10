import re
from typing import Dict, Any

class ContextAnalyzer:
    """
    Stage 5: Context Analyzer
    Deterministic, rule-based contextual understanding of *why* the number was spoken.
    """
    
    def __init__(self):
        # Maps regex patterns to Entity Types
        self.intent_patterns = {
            "OTP": [
                r"\b(otp|one time password|password|code|pin)\b"
            ],
            "BANK_ACCOUNT": [
                r"\b(account|bank account|ac|a/c|khata)\b"
            ],
            "UPI_ID": [
                r"\b(upi|gpay|google pay|phonepe|paytm)\b"
            ],
            "AADHAAR": [
                r"\b(aadhaar|adhar|aadhar|uid)\b"
            ],
            "PAN": [
                r"\b(pan|pan card)\b"
            ],
            "PHONE_NUMBER": [
                r"\b(phone|mobile|whatsapp|contact|call|number)\b",
                r"\b(ph|mob|no)\b"
            ]
        }
        
        self.compiled_patterns = {
            entity: [re.compile(p, re.IGNORECASE) for p in patterns]
            for entity, patterns in self.intent_patterns.items()
        }
        
    def analyze(self, full_text: str, span_start_idx: int, span_end_idx: int) -> Dict[str, Any]:
        """
        Analyzes context around a number span.
        Returns context dict with 'entity_type' and 'trigger_word'.
        """
        # Get window of words before and after
        tokens = full_text.split()
        window_start = max(0, span_start_idx - 10)
        window_end = min(len(tokens), span_end_idx + 10)
        
        context_text = " ".join(tokens[window_start:span_start_idx] + tokens[span_end_idx+1:window_end])
        
        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(context_text)
                if match:
                    return {
                        "entity_type": entity_type,
                        "trigger_word": match.group(0),
                        "context_text": context_text
                    }
                    
        # Default fallback
        return {
            "entity_type": "UNKNOWN_NUMBER",
            "trigger_word": None,
            "context_text": context_text
        }
