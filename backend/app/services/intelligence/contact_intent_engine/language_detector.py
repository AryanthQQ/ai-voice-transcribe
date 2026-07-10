from typing import Dict, Any

class LanguageDetector:
    """
    Identifies the primary language by evaluating token overlap with the YAML vocabularies.
    """
    def __init__(self, configs: Dict[str, Any]):
        self.configs = configs

    def detect(self, text: str, provided_lang: str = None) -> str:
        if provided_lang and provided_lang in self.configs:
            return provided_lang

        # Fallback heuristic: count keyword hits
        best_lang = "en"
        max_hits = -1
        
        for lang_code, config in self.configs.items():
            hits = 0
            if 'intents' not in config:
                continue
                
            for intent_name, intent_data in config['intents'].items():
                for word in intent_data.get('positive', []):
                    if word in text:
                        hits += 1
                        
            if hits > max_hits:
                max_hits = hits
                best_lang = lang_code
                
        # If no hits, default to english
        if max_hits == 0:
            return "en"
            
        return best_lang
