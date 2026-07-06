import os
import json
import urllib.request
import tempfile
import threading
from typing import Dict, Any

from app.core.logger import logger
from app.services.speech_service import speech_service
from app.services.diarize_service import diarize_service
from app.services.gemini_service import gemini_service
from app.services.transliterate_service import hindi_to_hinglish
from app.services.violation_service import check_for_violations
from app.services.email_service import send_violation_alert_email

# Singleton lock to ensure only one heavy analysis runs at a time (saves memory)
analysis_lock = threading.Lock()

def process_call_audio(adviser_id: str, user_id: str, voice_url: str) -> Dict[str, Any]:
    with analysis_lock:
        logger.info(f"Starting analysis for {voice_url}")
        temp_path = None
        try:
            # 1. Download audio file
            ext = voice_url.rsplit(".", 1)[-1].lower() if "." in voice_url else "mp3"
            ext = ext.split("?")[0]
            allowed_exts = {"mp3", "wav", "webm", "m4a", "ogg", "flac", "mp4", "aac"}
            if ext not in allowed_exts:
                ext = "mp3"
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
                req = urllib.request.Request(voice_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    temp_audio.write(response.read())
                temp_path = temp_audio.name
                
            # 2. Transcribe
            segments, info = speech_service.transcribe(temp_path)
            
            # 3. Diarize
            diarize_results = diarize_service.diarize(temp_path, num_speakers=2)
            
            # 4. Map speakers to text
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

            # 5. Gemini Processing
            summary_text = ""
            gemini_success = False
            
            if turns:
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
                except Exception as e:
                    logger.error(f"Gemini processing failed: {e}")

            if not gemini_success:
                for turn in turns:
                    turn["text"] = hindi_to_hinglish(turn.get("text", ""))
                    turn["english"] = turn["text"]
                    
            full_text = " ".join([t.get("text", "") for t in turns]).strip()
            
            # 6. Safety Checks & Alerts
            incidents = check_for_violations(turns)
            if incidents:
                logger.warning(f"Violations found for {adviser_id}! Triggering alert.")
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
                threading.Thread(target=send_violation_alert_email, args=(alert_data,)).start()
            
            return {
                "success": True,
                "transcript": full_text,
                "turns": turns,
                "language": info.language,
                "summary": summary_text,
                "incidents": incidents
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Worker failed: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
