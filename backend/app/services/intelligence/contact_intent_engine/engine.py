from typing import List, Dict, Any
import os

from .models import IntentInput, IntentResult
from .config_loader import ConfigLoader
from .cleaner import Cleaner
from .language_detector import LanguageDetector
from .detector import IntentDetector
from .normalizer import IntentNormalizer
from .confidence import ConfidenceEngine

class ContactIntentEngine:
    """
    Orchestrates the Contact Intent detection pipeline.
    """
    def __init__(self, config_dir: str = None):
        # 1. Load Configurations
        self.config_loader = ConfigLoader(config_dir)
        all_intents = self.config_loader.get_all_intents()
        
        # 2. Initialize Pipeline Stages
        self.cleaner = Cleaner()
        self.lang_detector = LanguageDetector(self.config_loader.configs)
        self.detector = IntentDetector(all_intents)
        self.normalizer = IntentNormalizer()
        self.confidence_engine = ConfidenceEngine()

    def process(self, segment: IntentInput) -> List[IntentResult]:
        results = []
        
        # Stage 1: Clean
        clean_text = self.cleaner.clean(segment.text)
        if not clean_text:
            return results
            
        # Stage 2: Detect Language
        lang = self.lang_detector.detect(clean_text, segment.detected_language)
        
        # Stage 3: Detect Intent (using cross-lingual flattened patterns)
        raw_detections = self.detector.detect(clean_text)
        if not raw_detections:
            return results
            
        # Stage 4: Normalize
        normalized = self.normalizer.normalize(raw_detections)
        
        # Stage 5: Confidence Scoring
        scored = self.confidence_engine.score(normalized)
        
        # Construct Final Result Objects
        for item in scored:
            # We don't have exact word-level timestamp alignment in this rule-based approach,
            # so we inherit the segment timestamps as a bounding box.
            result = IntentResult(
                intent=item["intent"],
                channel=item["channel"],
                action=item["action"],
                matched_text=item["matched_text"],
                confidence=item["confidence"],
                speaker=segment.speaker,
                timestamps=(segment.start, segment.end)
            )
            results.append(result)
            
        return results
