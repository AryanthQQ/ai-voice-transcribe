import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.core.logger import logger

def hindi_to_hinglish(text: str) -> str:
    """
    Accurately transliterates Devanagari text to Roman Hindi (Hinglish/ITRANS).
    """
    if not text:
        return text
        
    try:
        # Transliterate Devanagari to standard ITRANS (Roman)
        hinglish = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        
        # Clean up ITRANS-specific artifacts
        hinglish = hinglish.lower()
        hinglish = hinglish.replace('aa', 'a')
        hinglish = hinglish.replace('ii', 'i')
        hinglish = hinglish.replace('uu', 'u')
        
        # Clean up dots from ITRANS schema
        hinglish = hinglish.replace('.d', 'd')
        hinglish = hinglish.replace('.h', '')
        hinglish = hinglish.replace('.', '')
        
        # Strip residual mathematical or non-standard characters from transliteration
        hinglish = re.sub(r'[^a-zA-Z0-9\s]', '', hinglish)
        
        return hinglish
    except Exception as e:
        logger.error(f"Transliteration error: {e}")
        return text
