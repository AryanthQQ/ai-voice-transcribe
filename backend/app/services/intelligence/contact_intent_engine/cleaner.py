import re

class Cleaner:
    """
    Standardizes and sanitizes the raw transcript segment.
    """
    def clean(self, text: str) -> str:
        if not text:
            return ""
        
        # Lowercase
        cleaned = text.lower()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove special characters but keep alphanumeric and basic punctuation
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        
        return cleaned
