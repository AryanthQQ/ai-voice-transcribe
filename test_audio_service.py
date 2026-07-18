import sys
import os
import json
import time
from pathlib import Path
sys.path.append(str(Path('backend').resolve()))

import unittest
from unittest.mock import patch, MagicMock

from app.services.audio_service import audio_downloader, AudioDownloadError, InvalidUrlError, DownloadTimeoutError, UnsupportedFormatError, FileCorruptionError

class TestAudioDownloader(unittest.TestCase):
    @patch('app.services.audio_service.subprocess.run')
    @patch('app.services.audio_service.urllib.request.urlopen')
    def test_successful_download(self, mock_urlopen, mock_subprocess):
        # Mocking urlopen
        mock_response = MagicMock()
        mock_response.headers = {'Content-Length': '1024'}
        mock_response.read.return_value = b'fake audio data'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Mocking ffprobe output
        mock_sub_result = MagicMock()
        mock_sub_result.returncode = 0
        mock_sub_result.stdout = json.dumps({"format": {"format_name": "mp3", "duration": "10.5"}})
        mock_subprocess.return_value = mock_sub_result
        
        temp_dir_captured = None
        
        with audio_downloader.download_and_manage("http://example.com/audio.mp3") as (temp_path, metrics):
            self.assertTrue(os.path.exists(temp_path))
            temp_dir_captured = os.path.dirname(temp_path)
            self.assertEqual(metrics["retry_count"], 0)
            self.assertEqual(metrics["duration_sec"], 10.5)
            self.assertTrue(metrics["file_size_mb"] > 0)
            
        # Verify cleanup
        self.assertFalse(os.path.exists(temp_dir_captured))
        
    def test_invalid_url(self):
        with self.assertRaises(InvalidUrlError):
            with audio_downloader.download_and_manage("ftp://example.com/audio.mp3"):
                pass
                
    @patch('app.services.audio_service.time.sleep')
    @patch('app.services.audio_service.urllib.request.urlopen')
    def test_retry_on_timeout(self, mock_urlopen, mock_sleep):
        import urllib.error
        # Make it timeout 3 times
        mock_urlopen.side_effect = TimeoutError("Simulated timeout")
        
        with self.assertRaises(DownloadTimeoutError):
            with audio_downloader.download_and_manage("http://example.com/audio.mp3"):
                pass
                
        self.assertEqual(mock_urlopen.call_count, 3)

    @patch('app.services.audio_service.subprocess.run')
    @patch('app.services.audio_service.urllib.request.urlopen')
    def test_unsupported_format(self, mock_urlopen, mock_subprocess):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Length': '1024'}
        mock_response.read.return_value = b'fake pdf data'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Mocking ffprobe output with unsupported format
        mock_sub_result = MagicMock()
        mock_sub_result.returncode = 0
        mock_sub_result.stdout = json.dumps({"format": {"format_name": "pdf", "duration": "0"}})
        mock_subprocess.return_value = mock_sub_result
        
        with self.assertRaises(UnsupportedFormatError):
            with audio_downloader.download_and_manage("http://example.com/audio.mp3"):
                pass

if __name__ == '__main__':
    unittest.main()
