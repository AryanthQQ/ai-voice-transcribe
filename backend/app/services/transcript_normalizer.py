import re
from app.data.normalization_rules import NORMALIZATION_RULES

class TranscriptNormalizer:
    def __init__(self):
        self.compiled_patterns = []
        
        # 1. Compile word normalization rules
        for replacement, variants in NORMALIZATION_RULES.items():
            # Sort variants by length (longest first) to prevent partial substring matches 
            # (e.g. 'Instagram' matching before 'Insta')
            sorted_variants = sorted(variants, key=len, reverse=True)
            
            # Escape regex characters just in case, though variants are mostly plain text
            escaped_variants = [re.escape(v) for v in sorted_variants]
            
            # For English-only alphanumeric words, we could use \b, but since we're dealing with
            # mixed Hindi/English STT output where spaces are inconsistent, using longest-match-first
            # without strict \b is safer for cross-lingual boundary issues.
            # Using (?i) for case-insensitive matching.
            pattern_str = r'(?i)(' + '|'.join(escaped_variants) + r')'
            
            self.compiled_patterns.append((re.compile(pattern_str), replacement))
        
        # 2. Compile STT Noise Reduction Patterns
        self.duplicate_space_pattern = re.compile(r'\s+')
        self.duplicate_comma_pattern = re.compile(r',+')
        self.duplicate_period_pattern = re.compile(r'\.+')
        
        # 3. Compile Phone Number normalizer (removes spaces/dashes between digits)
        # Matches any space or dash that is immediately preceded by a digit and immediately followed by a digit.
        self.digit_separator_pattern = re.compile(r'(?<=\d)[\s-]+(?=\d)')

    def normalize(self, text: str) -> str:
        if not text:
            return text
            
        normalized = text
        
        # A. Word Normalization (WhatsApp, Telegram, etc.)
        for pattern, replacement in self.compiled_patterns:
            normalized = pattern.sub(replacement, normalized)
            
        # B. Digits Normalization (Collapse spaces and dashes between numbers)
        # e.g. "9 8 7" -> "987" or "98-76" -> "9876"
        # We run this in a loop in case of overlapping spaces if the regex engine doesn't consume all,
        # but the lookaround (?<=\d)[\s-]+(?=\d) safely consumes just the spaces.
        # Since [\s-]+ consumes multiple spaces/dashes at once, one pass is usually enough,
        # but if we have "9 8 7", after replacing "9 8", we get "98 7", so we might need to 
        # apply it iteratively if it doesn't match globally. 
        # Actually, python's re.sub replaces non-overlapping occurrences. 
        # For "9 8 7", replacing " " between 9 and 8 consumes the space, lookaheads don't consume characters.
        # So it will replace all occurrences in one pass!
        normalized = self.digit_separator_pattern.sub('', normalized)
        
        # C. Noise Reduction
        # Replace duplicate commas with a single comma
        normalized = self.duplicate_comma_pattern.sub(',', normalized)
        # Replace duplicate periods with a single period
        normalized = self.duplicate_period_pattern.sub('.', normalized)
        # Replace multiple spaces with a single space
        normalized = self.duplicate_space_pattern.sub(' ', normalized).strip()
        
        return normalized

# Singleton instance for easy import
transcript_normalizer = TranscriptNormalizer()
