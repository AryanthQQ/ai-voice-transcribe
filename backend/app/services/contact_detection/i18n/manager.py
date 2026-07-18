import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

class LanguageResourceManager:
    """
    Manages loading and caching of language-specific JSON resources and compiled regex patterns.
    """
    def __init__(self):
        # Cache format: cache[language][detector] = dict
        self._cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Regex cache format: regex_cache[language][detector][key] = compiled_pattern
        self._regex_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Path to the resources directory
        self._resources_dir = Path(__file__).parent / "resources"
        
        # Fallback chain configuration
        self._fallback_chain = {
            "hi": ["en"],
            "es": ["en"],
            # default fallback if not found
            "default": ["en"]
        }
        
    def _load_resource(self, language: str, detector_name: str) -> Dict[str, Any]:
        """Loads a JSON file for a given language and detector."""
        file_path = self._resources_dir / language / f"{detector_name}.json"
        if not file_path.exists():
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def get_resource(self, detector_name: str, key: str, language: Optional[str] = None) -> Any:
        """
        Fetch a specific key from the loaded resources for a detector.
        Follows the fallback chain if the key is not found.
        """
        lang = language or "en"
        
        # Try finding the resource in the current language or through the fallback chain
        languages_to_check = [lang] + self._fallback_chain.get(lang, self._fallback_chain["default"])
        # Remove duplicates preserving order
        languages_to_check = list(dict.fromkeys(languages_to_check))
        
        for l in languages_to_check:
            if l not in self._cache:
                self._cache[l] = {}
            if detector_name not in self._cache[l]:
                self._cache[l][detector_name] = self._load_resource(l, detector_name)
                
            resource = self._cache[l][detector_name].get(key)
            if resource is not None:
                return resource
                
        return None

    def get_compiled_regex(self, detector_name: str, regex_key: str, pattern_string: str, language: Optional[str] = None, flags=re.IGNORECASE) -> Any:
        """
        Compiles and caches a regular expression pattern so it doesn't rebuild on every request.
        """
        lang = language or "en"
        
        if lang not in self._regex_cache:
            self._regex_cache[lang] = {}
        if detector_name not in self._regex_cache[lang]:
            self._regex_cache[lang][detector_name] = {}
            
        if regex_key not in self._regex_cache[lang][detector_name]:
            self._regex_cache[lang][detector_name][regex_key] = re.compile(pattern_string, flags)
            
        return self._regex_cache[lang][detector_name][regex_key]

# Singleton instance to be used across the application
i18n_manager = LanguageResourceManager()
