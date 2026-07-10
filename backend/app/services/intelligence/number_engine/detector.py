from typing import List, Tuple
from .languages import get_all_languages

class Span:
    def __init__(self, tokens: List[str], start_idx: int, end_idx: int):
        self.tokens = tokens
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.raw_text = " ".join(tokens)

class NumberDetector:
    """
    Stage 3: Number Detector
    Identifies contiguous sequences of numeric words (including multipliers).
    """
    
    def __init__(self):
        self.languages = get_all_languages()
        self.all_keywords = set()
        for lang in self.languages:
            self.all_keywords.update(lang.digit_map.keys())
            self.all_keywords.update(lang.multipliers.keys())
            
        # We also need to handle multi-word multipliers like "do baar" or "two times"
        self.multi_word_keywords = {k for k in self.all_keywords if " " in k}
        
    def detect(self, cleaned_text: str) -> List[Span]:
        """
        Scans cleaned text for contiguous sequences of number words.
        Returns a list of Spans.
        """
        tokens = cleaned_text.split()
        spans = []
        
        current_span_tokens = []
        start_idx = -1
        
        i = 0
        while i < len(tokens):
            # Check for multi-word matches first (greedy match)
            matched_multi = False
            for mw_keyword in self.multi_word_keywords:
                mw_tokens = mw_keyword.split()
                mw_len = len(mw_tokens)
                if i + mw_len <= len(tokens):
                    if tokens[i:i+mw_len] == mw_tokens:
                        if not current_span_tokens:
                            start_idx = i
                        current_span_tokens.extend(mw_tokens)
                        i += mw_len
                        matched_multi = True
                        break
                        
            if matched_multi:
                continue
                
            # Single word match
            token = tokens[i]
            # Digits like "9876543210" might also be passed directly if the STT output raw numbers
            is_raw_digit = token.isdigit()
            
            if token in self.all_keywords or is_raw_digit:
                if not current_span_tokens:
                    start_idx = i
                current_span_tokens.append(token)
            else:
                if current_span_tokens:
                    # End of a sequence
                    # Only keep sequences that have at least some minimum length or are purely raw digits
                    # Actually, a single word "nine" might not be a phone number, but we'll let Validator filter it.
                    spans.append(Span(current_span_tokens, start_idx, i - 1))
                    current_span_tokens = []
            i += 1
            
        if current_span_tokens:
            spans.append(Span(current_span_tokens, start_idx, len(tokens) - 1))
            
        return spans
