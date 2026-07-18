import sys
import os
import time
import threading
from pathlib import Path
sys.path.append(str(Path('backend').resolve()))

from unittest.mock import patch, MagicMock
from app.services.worker_service import process_call_audio_async_modern
from app.core.config import settings

def test_modern_business_flow():
    with patch('app.services.worker_service.inference_pipeline') as mock_inf_pipeline, \
         patch('app.services.worker_service.audio_downloader') as mock_audio, \
         patch('app.services.worker_service.send_violation_alert_email') as mock_email, \
         patch('app.services.worker_service.job_service') as mock_job, \
         patch('app.services.worker_service.log_structured') as mock_log:
         
         # Mock audio downloader context manager
         mock_audio_cm = MagicMock()
         mock_audio_cm.__enter__.return_value = ('/tmp/fake.mp3', {'duration_sec': 60, 'file_size_mb': 1})
         mock_audio.download_and_manage.return_value = mock_audio_cm
         
         # Mock inference output with duplicates to test deduplication
         mock_inf_pipeline.run.return_value = {
             "language": "en",
             "transcript": "hello give me a call at 9876543210 and whatsapp me at 9876543210",
             "overall_risk": "high",
             "risk_score": 80,
             "violations": [
                 {"type": "phone_number", "text": "9876543210"},
                 {"type": "phone_number", "text": "9876543210"}
             ]
         }
         
         # To test async and non-blocking, we need the mock_email to take some time, but we don't want to block the main thread.
         def slow_email(*args, **kwargs):
             time.sleep(0.5)
         mock_email.side_effect = slow_email
         
         start_time = time.time()
         process_call_audio_async_modern("job1", "adv1", "user1", "http://example.com/audio.mp3")
         exec_time = time.time() - start_time
         
         # Since email is async, exec_time should be < 0.5s
         assert exec_time < 0.5, "Pipeline blocked on email sending!"
         
         # Verify job_service.update_job was called with completed status and correct result schema
         update_calls = mock_job.update_job.call_args_list
         completed_call = [c for c in update_calls if c[0][1] == 'completed'][0]
         
         result_data = completed_call[1].get('result') or completed_call[0][5]
         assert result_data['decision'] == 'BLOCK'
         assert result_data['processing_status'] == 'SUCCESS'
         assert result_data['email_triggered'] == True
         
         # Wait for email thread to finish
         time.sleep(1.0)
         
         # Verify email payload and deduplication
         mock_email.assert_called_once()
         alert_data = mock_email.call_args[0][0]
         assert alert_data['call_id'] == "adv1_user1_job1"
         assert alert_data['overall_risk'] == "high"
         assert alert_data['risk_score'] == 80
         # Deduplication check: although there were 2 phone_number violations, the types list should only have 1
         assert len(alert_data['violation_types']) == 1
         assert alert_data['violation_types'][0] == "phone_number"
         
test_modern_business_flow()
print('Business flow verification passed.')
