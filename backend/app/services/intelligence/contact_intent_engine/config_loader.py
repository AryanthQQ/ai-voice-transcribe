import os
import yaml
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_dir: str = None):
        if not config_dir:
            config_dir = os.path.join(os.path.dirname(__file__), 'languages')
        self.config_dir = config_dir
        self.configs = {}
        self.load_all_configs()

    def load_all_configs(self):
        """Loads all YAML files in the languages directory."""
        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")
            
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".yaml"):
                lang_code = filename.replace('.yaml', '')
                filepath = os.path.join(self.config_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.configs[lang_code] = yaml.safe_load(f)

    def get_config(self, lang_code: str) -> Dict[str, Any]:
        """Returns the configuration for a specific language code."""
        return self.configs.get(lang_code, {})

    def get_all_intents(self) -> Dict[str, Dict[str, Any]]:
        """
        Flattens and merges all languages into a unified intent structure for scanning.
        Structure: 
        {
            "WHATSAPP": {
                "action": "MESSAGE",
                "positive": ["whatsapp", "whatsapp karo", ...],
                "negative": ["download whatsapp", "whatsapp download karo", ...]
            }
        }
        """
        merged = {}
        for lang, config in self.configs.items():
            if 'intents' not in config:
                continue
                
            for intent_name, intent_data in config['intents'].items():
                if intent_name not in merged:
                    merged[intent_name] = {
                        "action": intent_data.get("action", "MESSAGE"),
                        "positive": [],
                        "negative": []
                    }
                merged[intent_name]["positive"].extend(intent_data.get("positive", []))
                merged[intent_name]["negative"].extend(intent_data.get("negative", []))
                
        # Deduplicate
        for intent_name in merged:
            merged[intent_name]["positive"] = list(set(merged[intent_name]["positive"]))
            merged[intent_name]["negative"] = list(set(merged[intent_name]["negative"]))
            
        return merged
