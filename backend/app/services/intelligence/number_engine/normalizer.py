from typing import List, Tuple
from .languages import get_all_languages

class NumberNormalizer:
    """
    Stage 4: Number Normalizer
    Converts spoken word sequences into absolute numeric strings.
    Translates multi-lingual sequences into strict digit strings.
    """
    
    def __init__(self):
        self.languages = get_all_languages()
        
        # Build unified mapping for fast lookup
        self.digit_map = {}
        self.multiplier_map = {}
        
        for lang in self.languages:
            # We assume no conflicts in meaning (e.g., "char" is 4 in Hindi/Marathi/Gujarati)
            self.digit_map.update(lang.digit_map)
            self.multiplier_map.update(lang.multipliers)
            
        # Add some base numbers that could be parsed
        for i in range(10):
            self.digit_map[str(i)] = str(i)
            
    def normalize(self, tokens: List[str]) -> Tuple[str, List[str]]:
        """
        Normalizes a list of digit tokens.
        Returns the normalized numeric string and the normalization path (for evidence).
        """
        result = []
        path = []
        
        i = 0
        while i < len(tokens):
            # Check for multi-word multipliers first (e.g., "do baar")
            matched_multi = False
            for mw_key, mw_val in self.multiplier_map.items():
                if " " in mw_key:
                    mw_tokens = mw_key.split()
                    mw_len = len(mw_tokens)
                    if i + mw_len <= len(tokens):
                        if tokens[i:i+mw_len] == mw_tokens:
                            # We found a multiplier, we need the NEXT token to multiply
                            if i + mw_len < len(tokens):
                                next_token = tokens[i + mw_len]
                                if next_token in self.digit_map:
                                    digit = self.digit_map[next_token]
                                    result.extend([digit] * mw_val)
                                    path.append(f"[{mw_key}:x{mw_val} {next_token}:{digit}]")
                                    i += mw_len + 1
                                    matched_multi = True
                                    break
                            
            if matched_multi:
                continue
                
            token = tokens[i]
            
            # Single-word multiplier (e.g., "double")
            if token in self.multiplier_map:
                multiplier = self.multiplier_map[token]
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    if next_token in self.digit_map:
                        digit = self.digit_map[next_token]
                        result.extend([digit] * multiplier)
                        path.append(f"[{token}:x{multiplier} {next_token}:{digit}]")
                        i += 2
                        continue
                        
            # Normal digit
            if token in self.digit_map:
                digit = self.digit_map[token]
                result.append(digit)
                path.append(f"[{token}:{digit}]")
                i += 1
                continue
                
            # Raw digit
            if token.isdigit():
                # Raw sequence like "9876543210"
                for d in token:
                    result.append(d)
                path.append(f"[{token}:raw]")
                i += 1
                continue
                
            # Unknown token (should be rare if detector worked correctly)
            path.append(f"[{token}:unknown]")
            i += 1
            
        return "".join(result), path
