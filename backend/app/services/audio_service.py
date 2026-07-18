import os
import time
import urllib.request
import urllib.error
import tempfile
import shutil
import json
import subprocess
from typing import Dict, Any, Tuple
from contextlib import contextmanager

from app.core.config import settings
from app.core.logger import logger

class AudioDownloadError(Exception):
    pass

class InvalidUrlError(AudioDownloadError):
    pass

class DownloadTimeoutError(AudioDownloadError):
    pass

class UnsupportedFormatError(AudioDownloadError):
    pass

class FileCorruptionError(AudioDownloadError):
    pass

class AudioDownloader:
    SUPPORTED_FORMATS = {'mp3', 'wav', 'm4a'}
    
    @contextmanager
    def download_and_manage(self, voice_url: str):
        """
        Context manager that creates a dedicated temp directory, downloads the file,
        validates it, and yields the final file path. 
        Cleans up the directory entirely in the finally block.
        """
        temp_dir = tempfile.mkdtemp(prefix="audio_dwl_")
        downloaded_path = None
        metrics = {
            "download_time_sec": 0,
            "retry_count": 0,
            "file_size_mb": 0.0,
            "duration_sec": 0.0
        }
        
        try:
            self._validate_url(voice_url)
            downloaded_path, metrics = self._download_with_retries(voice_url, temp_dir)
            self._validate_content(downloaded_path, metrics)
            yield downloaded_path, metrics
        finally:
            # Automatic cleanup of the dedicated temporary directory
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.error(f"Failed to clean up temp directory {temp_dir}: {e}")

    def _validate_url(self, url: str):
        if not url or not url.startswith(("http://", "https://")):
            raise InvalidUrlError("Invalid URL scheme. Must be HTTP or HTTPS.")

    def _download_with_retries(self, url: str, temp_dir: str) -> Tuple[str, Dict[str, Any]]:
        max_retries = 3
        retry_count = 0
        start_time = time.time()
        
        # We don't trust the URL extension but we use a generic bin extension first
        temp_file_path = os.path.join(temp_dir, "downloaded.tmp")
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > (settings.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024):
                        raise AudioDownloadError(f"File too large: exceeds {settings.MAX_AUDIO_FILE_SIZE_MB}MB limit.")
                        
                    with open(temp_file_path, 'wb') as f:
                        shutil.copyfileobj(response, f)
                        
                file_size_mb = os.path.getsize(temp_file_path) / (1024 * 1024)
                if file_size_mb == 0:
                    raise FileCorruptionError("Downloaded file is 0 bytes.")
                    
                metrics = {
                    "download_time_sec": round(time.time() - start_time, 2),
                    "retry_count": retry_count,
                    "file_size_mb": round(file_size_mb, 2)
                }
                return temp_file_path, metrics
                
            except urllib.error.HTTPError as e:
                if e.code in [403, 404]:
                    raise AudioDownloadError(f"HTTP {e.code}: Resource unavailable or forbidden. Not retrying.")
                # Otherwise, it might be 50x so we retry
                logger.warning(f"Download attempt {attempt+1} failed with HTTP {e.code}. Retrying...")
            except (urllib.error.URLError, TimeoutError, ConnectionResetError) as e:
                # Transient errors
                logger.warning(f"Download attempt {attempt+1} failed with transient error: {e}. Retrying...")
            except AudioDownloadError:
                raise # Re-raise known limits/errors without retrying
            except Exception as e:
                raise AudioDownloadError(f"Unexpected download error: {e}")
                
            retry_count += 1
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                
        raise DownloadTimeoutError(f"Failed to download audio after {max_retries} attempts.")

    def _validate_content(self, file_path: str, metrics: Dict[str, Any]):
        """
        Validates the audio content using ffprobe instead of trusting the file extension.
        Extracts format and duration.
        """
        try:
            cmd = [
                "ffprobe", 
                "-v", "error", 
                "-show_entries", "format=format_name,duration", 
                "-of", "json", 
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise FileCorruptionError("Failed to probe file content. The file might be corrupted or not a valid media file.")
                
            probe_data = json.loads(result.stdout)
            format_info = probe_data.get("format", {})
            
            format_names = format_info.get("format_name", "").split(",")
            # Ensure it overlaps with our supported types (ffprobe returns formats like 'mp3', 'wav', 'mov,mp4,m4a,3gp,3g2,mj2')
            is_supported = False
            for fmt in format_names:
                if fmt.lower() in self.SUPPORTED_FORMATS or "m4a" in fmt.lower() or "mp4" in fmt.lower() or "wav" in fmt.lower() or "mp3" in fmt.lower():
                    is_supported = True
                    break
                    
            if not is_supported:
                raise UnsupportedFormatError(f"Detected format '{format_info.get('format_name')}' is not supported. Supported: {self.SUPPORTED_FORMATS}")
                
            duration = float(format_info.get("duration", 0))
            if duration <= 0:
                raise FileCorruptionError("Audio duration is zero or unreadable. File may be corrupted.")
                
            if duration > settings.MAX_AUDIO_DURATION_SEC:
                raise AudioDownloadError(f"Audio duration ({duration}s) exceeds maximum allowed ({settings.MAX_AUDIO_DURATION_SEC}s).")
                
            metrics["duration_sec"] = round(duration, 2)
            
        except subprocess.TimeoutExpired:
            raise FileCorruptionError("Audio validation timed out. File might be corrupted.")
        except json.JSONDecodeError:
            raise FileCorruptionError("Failed to parse audio validation results. File might be corrupted.")
        except FileNotFoundError:
            logger.warning("ffprobe not found on system. Skipping deep content validation, falling back to basic checks.")
            # If ffprobe isn't installed, we can't do deep validation, but we assume it's valid if we reached here
            pass
            
audio_downloader = AudioDownloader()
