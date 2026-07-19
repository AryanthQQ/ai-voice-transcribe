from typing import List, Dict, Optional, Any
from .base import BaseContactDetector

DEBUG_CONTACT_DETECTORS = True

class ContactDetectionEngine:
    """
    Orchestrates contact detection plugins.
    """
    def __init__(self):
        self.detectors: List[BaseContactDetector] = []
        
    def register_detector(self, detector: BaseContactDetector):
        """Register a new detector plugin."""
        self.detectors.append(detector)
        
    def analyze(self, transcript: str, segments: Optional[List[Dict[str, Any]]] = None, language: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all registered detectors and return structured violations JSON.
        """
        all_violations = []
        for detector in self.detectors:
            try:
                violations = detector.detect(transcript, segments, language)
                all_violations.extend(violations)
                
                if DEBUG_CONTACT_DETECTORS:
                    print(f"\n[DEBUG] Detector Class: {detector.__class__.__name__}")
                    print(f"[DEBUG] Detector Name: {getattr(detector, 'name', 'unknown')}")
                    print(f"[DEBUG] Violations Count: {len(violations)}")
                    print(f"[DEBUG] Violations: {violations}")
                    
            except Exception as e:
                if DEBUG_CONTACT_DETECTORS:
                    print(f"\n[DEBUG] Detector Class: {detector.__class__.__name__}")
                    print(f"[DEBUG] Detector Name: {getattr(detector, 'name', 'unknown')}")
                    print(f"[DEBUG] Exception: {e}")
                # Log or handle detector failures gracefully
                pass
            
        # Sort by timestamp if available, else just return
        return {
            "violations": all_violations
        }
