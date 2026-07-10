from typing import Dict, Any, List

class IntentNormalizer:
    """
    Normalizes variations into standard internal categories.
    """
    def normalize(self, detected_intents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for det in detected_intents:
            normalized.append({
                "intent": "CONTACT_SHARE",
                "channel": det["intent_name"],
                "action": det["action"],
                "matched_text": det["matched_text"]
            })
        return normalized
