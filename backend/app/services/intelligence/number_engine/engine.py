from typing import List, Dict, Any
from .models.input import TranscriptSegment
from .models.output import EntityResult
from .cleaner import TranscriptCleaner
from .language_detector import LanguageDetector
from .detector import NumberDetector
from .normalizer import NumberNormalizer
from .context_analyzer import ContextAnalyzer
from .validator import Validator
from .confidence_engine import ConfidenceEngine
from .evidence_builder import EvidenceBuilder

class NumberEngine:
    """
    Main orchestration class for the Indian Number Intelligence Engine.
    Executes the 8-stage SRP pipeline.
    """
    
    def __init__(self):
        self.cleaner = TranscriptCleaner()
        self.language_detector = LanguageDetector()
        self.detector = NumberDetector()
        self.normalizer = NumberNormalizer()
        self.context_analyzer = ContextAnalyzer()
        self.validator = Validator()
        self.confidence_engine = ConfidenceEngine()
        self.evidence_builder = EvidenceBuilder()

    def process_segment(self, segment: TranscriptSegment) -> List[EntityResult]:
        """
        Processes a single transcript segment and extracts entities.
        """
        results = []
        
        # Stage 1: Clean
        cleaned_text = self.cleaner.clean(segment.text)
        
        # Stage 3: Detect number spans (we do this first to find tokens for Stage 2)
        spans = self.detector.detect(cleaned_text)
        
        for span in spans:
            # Stage 2: Language Detection
            predominant_lang = self.language_detector.detect(span.tokens)
            if not predominant_lang:
                predominant_lang = "unknown"
                
            lang_confidence = self.language_detector.get_language_confidence(span.tokens, predominant_lang)
            
            # Stage 4: Normalize
            normalized_value, norm_path = self.normalizer.normalize(span.tokens)
            if not normalized_value:
                continue
                
            # Stage 5: Context Analyzer
            context_dict = self.context_analyzer.analyze(cleaned_text, span.start_idx, span.end_idx)
            entity_type_guess = context_dict.get("entity_type", "UNKNOWN_NUMBER")
            
            # Stage 6: Validator
            validation_dict = self.validator.validate(normalized_value, entity_type_guess)
            
            final_entity_type = validation_dict.get("inferred_type", entity_type_guess)
            is_valid = validation_dict.get("is_valid", False)
            
            # Stage 7: Confidence
            final_confidence = self.confidence_engine.calculate(
                whisper_confidence=segment.confidence,
                language_confidence=lang_confidence,
                context_matched=bool(context_dict.get("trigger_word")),
                validation_passed=is_valid
            )
            
            # Stage 8: Evidence Builder
            evidence_dict = self.evidence_builder.build(
                raw_text=span.raw_text,
                span_tokens=span.tokens,
                normalization_path=norm_path,
                language=predominant_lang,
                context_dict=context_dict,
                validation_dict=validation_dict
            )
            
            # Create Result
            # Estimate timestamps linearly based on tokens
            total_tokens = len(cleaned_text.split())
            if total_tokens > 0:
                time_per_token = (segment.end - segment.start) / total_tokens
                span_start_time = segment.start + (span.start_idx * time_per_token)
                span_end_time = segment.start + ((span.end_idx + 1) * time_per_token)
            else:
                span_start_time = segment.start
                span_end_time = segment.end
                
            result = EntityResult(
                entity_type=final_entity_type,
                normalized_value=normalized_value,
                raw_text=span.raw_text,
                speaker=segment.speaker,
                timestamps=(span_start_time, span_end_time),
                language=predominant_lang,
                confidence=final_confidence,
                evidence=evidence_dict,
                validation_result=validation_dict,
                context=context_dict
            )
            results.append(result)
            
        return results

    def extract_entities(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Public API for the engine.
        Accepts raw dictionaries, parses them into Typed Models, processes, and returns dicts.
        """
        all_results = []
        for seg_dict in segments:
            try:
                segment = TranscriptSegment(**seg_dict)
                extracted = self.process_segment(segment)
                for ent in extracted:
                    all_results.append(ent.model_dump())
            except Exception as e:
                # Log or handle parsing error
                pass
                
        return all_results
