from typing import List, Dict, Optional
from collections import Counter
from .languages import get_all_languages

class LanguageDetector:
    """
    Stage 2: Language Detection
    Identifies the predominant language of the digit words within a sequence of text.
    """
    
    def __init__(self):
        self.languages = get_all_languages()
        
    def detect(self, tokens: List[str]) -> Optional[str]:
        """
        Detects the predominant language of the tokens that are recognized as digit words.
        Returns the language code (e.g., 'en', 'hi') or None if no digit words are found.
        """
        lang_counts = Counter()
        
        for token in tokens:
            for lang in self.languages:
                if token in lang.digit_map or token in lang.multipliers:
                    lang_counts[lang.code] += 1
                    
        if not lang_counts:
            return None
            
        # Return the language with the highest count
        most_common = lang_counts.most_common(1)[0][0]
        return most_common

    def get_language_confidence(self, tokens: List[str], primary_lang: str) -> float:
        """
        Calculates purity. 1.0 if all digit words belong to the primary_lang.
        Less than 1.0 if there's heavy code-switching mid-number.
        """
        total_digit_words = 0
        primary_lang_words = 0
        
        primary_lang_def = next((l for l in self.languages if l.code == primary_lang), None)
        if not primary_lang_def:
            return 0.0

        for token in tokens:
            is_digit_word = False
            is_primary = False
            
            # Check if it's a digit word in ANY language
            for lang in self.languages:
                if token in lang.digit_map or token in lang.multipliers:
                    is_digit_word = True
                    break
            
            if is_digit_word:
                total_digit_words += 1
                if token in primary_lang_def.digit_map or token in primary_lang_def.multipliers:
                    is_primary = True
            
            if is_primary:
                primary_lang_words += 1
                
        if total_digit_words == 0:
            return 1.0
            
        return primary_lang_words / total_digit_words
