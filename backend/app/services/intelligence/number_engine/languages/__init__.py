from typing import Dict, List, Set

class LanguageDefinition:
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
        self.digit_map: Dict[str, str] = {}
        self.multipliers: Dict[str, int] = {}
        self.noise_words: Set[str] = set()

    def add_digits(self, mappings: Dict[str, str]):
        self.digit_map.update(mappings)

    def add_multipliers(self, mappings: Dict[str, int]):
        self.multipliers.update(mappings)

    def add_noise(self, words: List[str]):
        self.noise_words.update(words)

# Global Registry
_REGISTRY: Dict[str, LanguageDefinition] = {}

def register_language(lang_def: LanguageDefinition):
    _REGISTRY[lang_def.code] = lang_def

def get_language(code: str) -> LanguageDefinition:
    return _REGISTRY.get(code)

def get_all_languages() -> List[LanguageDefinition]:
    return list(_REGISTRY.values())

# Auto-register default languages
from . import en, hi, mr, gu

