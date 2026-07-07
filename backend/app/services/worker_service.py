import os
import json
import urllib.request
import tempfile
import threading
import time
from typing import Dict, Any

from app.core.logger import logger
from app.services.speech_service import speech_service
from app.services.diarize_service import diarize_service
from app.services.gemini_service import gemini_service
from app.services.transliterate_service import hindi_to_hinglish
from app.services.violation_service import check_for_violations
from app.services.email_service import send_violation_alert_email
from app.services.job_service import job_service
from app.services.metrics_service import metrics_service

# Singleton lock to ensure only one heavy analysis runs at a time (saves memory)
analysis_lock = threading.Lock()

def process_call_audio_async(job_id: str, adviser_id: str, user_id: str, voice_url: str):
    """
    Background worker that updates job state and metrics.
    """
    start_total = time.time()
    
    def update(status, progress, stage):
        elapsed = time.time() - start_total
        job_service.update_job(job_id, status, progress, stage, f"{elapsed:.2f} sec")

    try:
        with analysis_lock:
            # Downloading 15%
            update("downloading", 15, "Downloading Audio")
            logger.info(f"[Job {job_id}] Starting analysis for {voice_url}")
            temp_path = None
            
            ext = voice_url.rsplit(".", 1)[-1].lower() if "." in voice_url else "mp3"
            ext = ext.split("?")[0]
            allowed_exts = {"mp3", "wav", "webm", "m4a", "ogg", "flac", "mp4", "aac"}
            if ext not in allowed_exts:
                ext = "mp3"
                
            # Validation 20%
            update("validating", 20, "Validating Audio")
            if not voice_url.startswith(("http://", "https://")):
                raise ValueError("Invalid URL scheme. Must be HTTP or HTTPS.")
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            head_req = urllib.request.Request(voice_url, headers=headers, method='HEAD')
            
            max_retries = 3
            download_success = False
            
            for attempt in range(max_retries):
                try:
                    with urllib.request.urlopen(head_req, timeout=10) as head_resp:
                        content_length = head_resp.headers.get('Content-Length')
                        if content_length and int(content_length) > 50 * 1024 * 1024:
                            raise ValueError(f"File too large: {int(content_length) / (1024*1024):.2f}MB > 50MB limit")
                        
                        content_type = head_resp.headers.get('Content-Type', '')
                        if content_type and not (content_type.startswith('audio/') or content_type.startswith('video/') or 'octet-stream' in content_type):
                            raise ValueError(f"Invalid Content-Type: {content_type}")
                            
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
                        req = urllib.request.Request(voice_url, headers=headers)
                        with urllib.request.urlopen(req, timeout=15) as response:
                            temp_audio.write(response.read())
                        temp_path = temp_audio.name
                        
                    download_success = True
                    break
                except Exception as e:
                    if "File too large" in str(e) or "Invalid Content-Type" in str(e) or "Invalid URL" in str(e):
                        raise e
                    logger.warning(f"[Job {job_id}] Download attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(2)
                    
            if not download_success:
                raise Exception("Failed to download audio after maximum retries.")
                
            file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            logger.info(f"[Job {job_id}] Downloaded audio size: {file_size_mb:.2f} MB")
                
            # Transcribing 45%
            update("transcribing", 45, "Whisper Transcription")
            start_transcribe = time.time()
            segments, info = speech_service.transcribe(temp_path)
            time_transcribe = time.time() - start_transcribe
            logger.info(f"[Job {job_id}] Transcription Time: {time_transcribe:.2f}s")
            
            # Diarization 65%
            update("speaker_diarization", 65, "Speaker Diarization")
            start_diarize = time.time()
            diarize_results = diarize_service.diarize(temp_path, num_speakers=2)
            time_diarize = time.time() - start_diarize
            logger.info(f"[Job {job_id}] Diarization Time: {time_diarize:.2f}s")
            
            turns = []
            for seg in segments:
                midpoint = (seg["start"] + seg["end"]) / 2.0
                speaker = "SPEAKER_00"
                for d in diarize_results:
                    if d["start"] <= midpoint <= d["end"]:
                        speaker = d["speaker"]
                        break
                        
                mins = int(seg["start"] // 60)
                secs = int(seg["start"] % 60)
                
                if turns and turns[-1]["speaker"] == speaker:
                    turns[-1]["text"] += " " + seg["text"]
                else:
                    turns.append({
                        "speaker": speaker,
                        "text": seg["text"],
                        "time": f"{mins}:{secs:02d}"
                    })

            # Gemini 85%
            update("gemini_analysis", 85, "Gemini Analysis")
            start_gemini = time.time()
            summary_text = ""
            gemini_success = False
            
            if turns:
                for attempt in range(max_retries):
                    try:
                        prompt = f"""
Analyze this call transcript where the text is in Devanagari script (Hindi/Marathi/etc.).
For each turn, you must:
1. Transliterate the "text" field into clean, modern, natural Roman Hinglish (e.g. convert "लड़की" to "ladki", "व्हाट्सएप" to "whatsapp", "स्कैनर" to "scanner", "प्रॉब्लम" to "problem"). Do NOT use academic dot notation.
2. Translate the "text" field into professional English and put it in a new field called "english".
Return ONLY a valid JSON array of objects with exactly "speaker", "time", "text" (for Roman Hinglish), and "english" (for English translation) fields.
Transcript:
{json.dumps(turns)}
"""
                        resp_text = gemini_service.generate_text(prompt)
                        if resp_text.startswith("```json"): resp_text = resp_text[7:]
                        if resp_text.startswith("```"): resp_text = resp_text[3:]
                        if resp_text.endswith("```"): resp_text = resp_text[:-3]
                        
                        translated_turns = json.loads(resp_text.strip())
                        if isinstance(translated_turns, list):
                            turns = translated_turns
                            gemini_success = True
                            
                        summary_prompt = f"Summarize this call in 2-3 sentences based on the following transcript:\n{json.dumps(turns)}"
                        summary_text = gemini_service.generate_text(summary_prompt)
                        break
                    except Exception as e:
                        logger.error(f"[Job {job_id}] Gemini processing attempt {attempt+1} failed: {e}")
                        time.sleep(2)
            
            time_gemini = time.time() - start_gemini
            logger.info(f"[Job {job_id}] Gemini Time: {time_gemini:.2f}s")

            if not gemini_success:
                for turn in turns:
                    turn["text"] = hindi_to_hinglish(turn.get("text", ""))
                    turn["english"] = turn["text"]
                    
            full_text = " ".join([t.get("text", "") for t in turns]).strip()
            
            # Moderation 92%
            update("moderation", 92, "Content Moderation")
            start_mod = time.time()
            incidents = check_for_violations(turns)
            
            # Gender 97%
            update("gender_detection", 97, "Gender Detection")
            # Note: Add actual gender detection hook here if required in the future.
            
            # Email (SMTP) happens async inside the violation service normally, but we can do it directly.
            update("email", 98, "Email Alerts")
            if incidents:
                logger.warning(f"[Job {job_id}] Violations found for {adviser_id}! Triggering alert.")
                all_violations = []
                for inc in incidents:
                    all_violations.extend(inc["violations"])
                
                alert_data = {
                    "user_id": user_id,
                    "adviser_id": adviser_id,
                    "violations": list(set(all_violations)),
                    "incidents": incidents,
                    "transcript": full_text,
                    "audio_url": voice_url
                }
                
                def send_email_with_retry():
                    for attempt in range(max_retries):
                        try:
                            send_violation_alert_email(alert_data)
                            break
                        except Exception as e:
                            logger.error(f"[Job {job_id}] SMTP attempt {attempt+1} failed: {e}")
                            time.sleep(2)
                            
                threading.Thread(target=send_email_with_retry).start()
            
            time_mod = time.time() - start_mod
            logger.info(f"[Job {job_id}] Moderation & Alerting Time: {time_mod:.2f}s")
            
            total_time = time.time() - start_total
            logger.info(f"[Job {job_id}] Total Processing Time: {total_time:.2f}s")
            
            result_data = {
                "success": True,
                "transcript": full_text,
                "turns": turns,
                "language": getattr(info, "language", "en"),
                "summary": summary_text,
                "incidents": incidents
            }
            
            # Completed 100%
            job_service.update_job(job_id, "completed", 100, "Completed", f"{total_time:.2f} sec", result=result_data)
            metrics_service.record_job(success=True, processing_time_sec=total_time)
            
    except Exception as e:
        total_time = time.time() - start_total
        logger.error(f"[Job {job_id}] Worker failed processing {voice_url}: {e}")
        error_data = {
            "code": "WORKER_PROCESSING_ERROR",
            "message": "Failed to process the audio call.",
            "details": str(e)
        }
        job_service.update_job(job_id, "failed", 100, "Failed", f"{total_time:.2f} sec", error=error_data)
        metrics_service.record_job(success=False, processing_time_sec=total_time)
        
    finally:
        # Cleanup
        if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.info(f"[Job {job_id}] Deleted temporary audio file {temp_path}")
            except Exception as e:
                logger.error(f"[Job {job_id}] Failed to delete temp file {temp_path}: {e}")
