from typing import Dict, Any, List

class ConfidenceEngine:
    """
    Calculates a confidence score based on pattern specificity and word count.
    """
    def score(self, normalized_intents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for intent in normalized_intents:
            matched_text = intent["matched_text"]
            word_count = len(matched_text.split())
            
            # Simple heuristic:
            # 1 word match (e.g. "whatsapp") -> 0.7 confidence
            # 2 word match (e.g. "whatsapp karo") -> 0.85 confidence
            # 3+ word match (e.g. "message me on whatsapp") -> 0.95 confidence
            if word_count == 1:
                confidence = 0.70
            elif word_count == 2:
                confidence = 0.85
            else:
                confidence = 0.95
                
            intent["confidence"] = confidence
            scored.append(intent)
            
        return scored
