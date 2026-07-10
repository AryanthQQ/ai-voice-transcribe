import re

class TranscriptCleaner:
    """
    Stage 1: Normalizes raw Whisper text.
    Removes punctuation, handles hyphenated number words (e.g., "twenty-two"),
    standardizes casing, and filters non-alphanumeric noise.
    """
    
    def __init__(self):
        # Basic cleanup patterns
        self.punctuation_pattern = re.compile(r'[^\w\s\-]')
        
        # Hyphenated words often mapped directly in some systems,
        # but here we might want to split them or keep them based on language definition.
        # For our simple word-by-word mapping, replacing hyphens with spaces is usually best.
        
    def clean(self, raw_text: str) -> str:
        text = raw_text.lower()
        
        # Remove standard punctuation
        text = self.punctuation_pattern.sub(' ', text)
        
        # Replace hyphens with spaces (so "twenty-two" becomes "twenty two")
        text = text.replace('-', ' ')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
