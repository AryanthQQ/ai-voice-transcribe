import sys
import json
import time
from pathlib import Path
sys.path.append(str(Path('backend').resolve()))

from app.services.inference_pipeline import inference_pipeline

import unittest
from unittest.mock import patch

class TestModernPipeline(unittest.TestCase):
    @patch('app.services.inference_pipeline.speech_service.transcribe')
    def test_pipeline_execution(self, mock_transcribe):
        class InfoMock:
            language = "hi"
            
        mock_transcribe.return_value = (
            [
                {"start": 0.0, "end": 2.0, "text": "mera number 9876543210 hai "},
                {"start": 2.0, "end": 4.0, "text": "Contact me on email"}
            ],
            InfoMock()
        )
        
        result = inference_pipeline.run("test_call_123", "fake_audio.wav")
        
        # Verify schema
        self.assertIn("call_id", result)
        self.assertEqual(result["call_id"], "test_call_123")
        self.assertIn("language", result)
        self.assertEqual(result["language"], "hi")
        self.assertIn("transcript", result)
        self.assertEqual(result["transcript"], "mera number 9876543210 hai Contact me on email")
        self.assertIn("overall_risk", result)
        self.assertIn("risk_score", result)
        self.assertIn("violations", result)
        self.assertIn("pipeline_metrics", result)
        self.assertIn("response_time_sec", result["pipeline_metrics"])
        self.assertIn("memory_usage_mb", result["pipeline_metrics"])
        
        # We expect a phone number violation and an email violation
        violations = result["violations"]
        types = [v["type"] for v in violations]
        self.assertIn("phone_number", types)
        self.assertIn("email", types)
        
        print("Pipeline Result:")
        print(json.dumps(result, indent=2))
        
    @patch('app.services.inference_pipeline.speech_service.transcribe')
    def test_pipeline_exception_handling(self, mock_transcribe):
        mock_transcribe.side_effect = Exception("Mocked STT Failure")
        
        result = inference_pipeline.run("test_call_error", "fake_audio.wav")
        
        self.assertEqual(result["overall_risk"], "error")
        self.assertEqual(result["risk_score"], 0)
        self.assertIn("Mocked STT Failure", result["error"])
        self.assertIn("pipeline_metrics", result)

if __name__ == '__main__':
    unittest.main()
