import time
import os
import psutil
from typing import Dict, Any

from app.core.logger import logger
from app.services.speech_service import speech_service
from app.services.contact_detection import get_engine as get_contact_engine
from app.services.compliance.engine import ComplianceEngine
from app.services.transcript_normalizer import transcript_normalizer

DEBUG_NORMALIZER = True

class InferencePipeline:
    def __init__(self):
        self.contact_engine = get_contact_engine()
        self.compliance_engine = ComplianceEngine()

    def run(self, call_id: str, audio_path: str) -> Dict[str, Any]:
        """
        Executes the modern, streamlined inference pipeline.
        Audio -> STT -> ContactDetection -> ComplianceEngine -> JSON
        """
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        
        try:
            # 1. Speech-to-Text
            stt_start = time.time()
            segments, info = speech_service.transcribe(audio_path)
            language = getattr(info, "language", "en") if info else "en"
            
            # Reconstruct transcript
            transcript = " ".join([seg.get("text", "").strip() for seg in segments])
            stt_time = time.time() - stt_start
            logger.info(f"[Pipeline] STT complete in {stt_time:.2f}s")
            
            # Normalize transcript before passing to Contact Detection
            normalized_transcript = transcript_normalizer.normalize(transcript)
            
            if DEBUG_NORMALIZER:
                try:
                    os.makedirs("logs", exist_ok=True)
                    with open("logs/normalizer_debug.txt", "w", encoding="utf-8") as f:
                        f.write("========== ORIGINAL ==========\n")
                        f.write(transcript + "\n\n")
                        f.write("========== NORMALIZED ==========\n")
                        f.write(normalized_transcript + "\n")
                except Exception as e:
                    logger.warning(f"Failed to write normalizer debug file: {e}")

            
            # 2. Contact Detection
            contact_start = time.time()
            contact_results = self.contact_engine.analyze(normalized_transcript, segments, language)
            raw_violations = contact_results.get("violations", [])
            contact_time = time.time() - contact_start
            logger.info(f"[Pipeline] Contact detection complete in {contact_time:.2f}s")
            
            # 3. Compliance Engine
            compliance_start = time.time()
            compliance_report = self.compliance_engine.process_violations(call_id, raw_violations)
            compliance_time = time.time() - compliance_start
            logger.info(f"[Pipeline] Compliance engine complete in {compliance_time:.2f}s")
            
            # Merging transcript and language into the compliance report
            result = compliance_report
            result["language"] = language
            result["transcript"] = transcript
            
            # Backwards compatibility
            result["success"] = True
            result["turns"] = []
            result["incidents"] = []
            result["trust_and_safety"] = {
                "overall_risk": result.get("overall_risk", "low"),
                "overall_action": "ALLOW",
                "turn_analysis": []
            }
            
            # Metrics
            total_time = time.time() - start_time
            end_mem = process.memory_info().rss
            mem_used_mb = (end_mem - start_mem) / (1024 * 1024)
            
            result["pipeline_metrics"] = {
                "response_time_sec": round(total_time, 2),
                "memory_usage_mb": round(mem_used_mb, 2)
            }
            
            logger.info(f"[Pipeline] Total execution time: {total_time:.2f}s, Memory Delta: {mem_used_mb:.2f}MB")
            
            return result
            
        except Exception as e:
            logger.error(f"[Pipeline] Execution failed: {str(e)}")
            total_time = time.time() - start_time
            return {
                "call_id": call_id,
                "language": "unknown",
                "transcript": "",
                "overall_risk": "error",
                "risk_score": 0,
                "violations": [],
                "error": str(e),
                "pipeline_metrics": {
                    "response_time_sec": round(total_time, 2)
                }
            }

# Singleton instance
inference_pipeline = InferencePipeline()
