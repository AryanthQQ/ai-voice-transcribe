from typing import Dict, Any, List, Tuple
import re

class IntentDetector:
    """
    Scans the text using the YAML-driven patterns to extract potential contact intents 
    while strictly discarding false positives.
    """
    def __init__(self, all_intents: Dict[str, Dict[str, Any]]):
        self.all_intents = all_intents

    def detect(self, text: str) -> List[Dict[str, Any]]:
        detected_intents = []
        
        for intent_name, intent_data in self.all_intents.items():
            # Check negative constraints first
            is_false_positive = False
            for neg in intent_data.get('negative', []):
                # Use regex word boundaries for precise matching
                if re.search(r'\b' + re.escape(neg) + r'\b', text):
                    is_false_positive = True
                    break
                    
            if is_false_positive:
                continue
                
            # Check positive constraints
            best_match = None
            max_len = -1
            
            for pos in intent_data.get('positive', []):
                # Search for the positive keyword
                match = re.search(r'\b' + re.escape(pos) + r'\b', text)
                if match:
                    # Prefer the longest match (e.g. "message me on whatsapp" > "whatsapp")
                    if len(pos) > max_len:
                        max_len = len(pos)
                        best_match = pos
                        
            if best_match:
                detected_intents.append({
                    "intent_name": intent_name,
                    "action": intent_data.get('action'),
                    "matched_text": best_match
                })
                
        # Deduplicate overlapping matches
        # Sort by matched_text length descending so we keep the longest match
        detected_intents.sort(key=lambda x: len(x["matched_text"]), reverse=True)
        
        final_intents = []
        for det in detected_intents:
            # Check if this matched_text is a substring of any already accepted matched_text
            is_subsumed = False
            for accepted in final_intents:
                if det["matched_text"] in accepted["matched_text"]:
                    is_subsumed = True
                    break
            
            if not is_subsumed:
                final_intents.append(det)
                
        return final_intents
