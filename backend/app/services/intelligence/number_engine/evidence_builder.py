from typing import List, Dict, Any

class EvidenceBuilder:
    """
    Stage 8: Evidence Builder
    Constructs the audit trail for explainability.
    """
    
    def build(self, 
              raw_text: str, 
              span_tokens: List[str], 
              normalization_path: List[str], 
              language: str, 
              context_dict: Dict[str, Any],
              validation_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds the structured evidence dictionary.
        """
        return {
            "original_transcript_snippet": raw_text,
            "matched_words": span_tokens,
            "normalization_path": normalization_path,
            "predominant_language": language,
            "context_trigger": context_dict.get("trigger_word"),
            "context_window": context_dict.get("context_text"),
            "validation_reason": validation_dict.get("reason")
        }
