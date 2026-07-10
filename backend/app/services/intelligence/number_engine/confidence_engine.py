class ConfidenceEngine:
    """
    Stage 7: Confidence Engine
    Calculates a unified, heavily-weighted confidence score.
    """
    
    def calculate(self, 
                  whisper_confidence: float, 
                  language_confidence: float, 
                  context_matched: bool, 
                  validation_passed: bool) -> float:
        """
        Calculates the final confidence score based on various factors.
        """
        # Base is whisper confidence
        score = whisper_confidence
        
        # Penalize if language is heavily mixed (e.g. language_confidence < 0.5)
        # We apply a slight penalty for code-switching, but not too much since it's common in India.
        if language_confidence < 0.8:
            score *= 0.95
            
        if language_confidence < 0.5:
            score *= 0.9
            
        # Boost if context matched
        if context_matched:
            # E.g. found "whatsapp number" right before the digits
            score = min(1.0, score * 1.1)
            
        # Heavy penalty if validation failed
        if not validation_passed:
            # E.g., only 7 digits found for a mobile number
            score *= 0.3
            
        return round(score, 3)
