import sys
import io
import os
# Force UTF-8 encoding on Windows to prevent 'charmap' codec errors with Hindi/Urdu/regional Unicode text
os.environ["PYTHONUTF8"] = "1"
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import os
# CRITICAL FIX for silent crashes:
# faster-whisper (CT2) and other libs both use OpenMP.
# On Windows, loading multiple OpenMP runtimes causes a silent exit code 1 crash.
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "4" # limit threads to prevent CPU locking

import tempfile
import json
import subprocess
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI()

# Allow CORS for localhost frontend (must be added BEFORE routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "SpeechIQ AI Backend is running successfully!"}

# large-v3 for best accuracy
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"

print(f"Loading Faster-Whisper Model: base on {device.upper()} ({compute_type})...")
model = WhisperModel("base", device=device, compute_type=compute_type)
print("Model loaded successfully!")

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("WARNING: HF_TOKEN not found in .env.")

from google import genai

client = None
gcp_cred_path = os.path.join(os.path.dirname(__file__), "gcp-credentials.json")
if os.path.exists(gcp_cred_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_cred_path
    try:
        with open(gcp_cred_path, "r") as f:
            cred_data = json.load(f)
            project_id = cred_data.get("project_id", "ai-modal-492711")
        client = genai.Client(vertexai=True, project=project_id, location="us-central1")
        print("[GEMINI] genai client initialized successfully!")
    except Exception as e:
        print("[GEMINI] Failed to initialize genai client:", e)

def call_gemini(prompt: str, model="gemini-2.5-flash-lite") -> str:
    if not client:
        raise ValueError("Gemini client not initialized")
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text.strip()

import numpy as np
def fast_diarize(audio_path: str, whisper_segments: list) -> list:
    """
    Groups segments into 2 speakers using K-Means on MFCCs.
    """
    import librosa
    import numpy as np
    from sklearn.cluster import KMeans

    if not whisper_segments:
        return []

    print("fast_diarize: Loading audio...", flush=True)
    try:
        y, sr = librosa.load(audio_path, sr=16000)
    except Exception as e:
        print(f"librosa.load failed: {e}", flush=True)
        raise
    
    print("fast_diarize: Audio loaded. Extracting features...", flush=True)
    features = []
    for seg in whisper_segments:
        start_sample = int(seg['start'] * sr)
        end_sample = int(seg['end'] * sr)
        chunk = y[start_sample:end_sample]
        if len(chunk) == 0:
            features.append(np.zeros(13))
            continue
        try:
            mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
            features.append(np.mean(mfcc, axis=1))
        except Exception as e:
            print(f"mfcc failed: {e}", flush=True)
            features.append(np.zeros(13))

    X = np.array(features)
    
    print("fast_diarize: Running KMeans...", flush=True)
    try:
        kmeans = KMeans(n_clusters=2, n_init=10, random_state=0)
        labels = kmeans.fit_predict(X)
    except Exception as e:
        print(f"KMeans failed: {e}", flush=True)
        labels = np.zeros(len(whisper_segments))
        
    print("fast_diarize: KMeans finished.", flush=True)
    
    turns = []
    for i, seg in enumerate(whisper_segments):
        speaker = "agent" if labels[i] == 0 else "customer"
        mins = int(seg["start"] // 60)
        secs = int(seg["start"] % 60)
        
        # Merge consecutive segments from the same speaker
        if turns and turns[-1]["speaker"] == speaker:
            turns[-1]["text"] += " " + seg["text"]
        else:
            turns.append({
                "speaker": speaker,
                "text": seg["text"],
                "time": f"{mins}:{secs:02d}"
            })
            
    return turns

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form(None),
    prompt: str = Form(None),
    translate: str = Form("true")
):
    temp_path = None
    try:
        # ── FIX 1: Use correct file extension from uploaded filename ─────────
        # Hardcoded .mp3 was causing Whisper to misread WebM/WAV/M4A files
        original_name = file.filename or "audio.mp3"
        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else "mp3"
        allowed_exts = {"mp3", "wav", "webm", "m4a", "ogg", "flac", "mp4", "aac"}
        if ext not in allowed_exts:
            ext = "mp3"  # safe fallback
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
            temp_audio.write(await file.read())
            temp_path = temp_audio.name

        file_size_kb = os.path.getsize(temp_path) / 1024
        print(f"Transcribing: {original_name} ({file_size_kb:.1f} KB), lang={language}, ext=.{ext}")
        
        if not prompt:
            prompt = "हाँ, ठीक है, जी, अच्छा।"

        # ── FIX 2: Disable aggressive VAD — it was silently dropping valid audio ─
        # vad_filter=True was cutting out short pauses and quiet voices.
        # We keep it False; Whisper's own silence handling is sufficient.
        segments_gen, info = model.transcribe(
            temp_path,
            language=language if language and language != "auto" else None,
            initial_prompt=prompt,
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            no_speech_threshold=0.6,
            vad_filter=False,   # ← was True; caused empty transcripts
            beam_size=5,
        )

        detected_lang = info.language
        print(f"Detected language: {detected_lang} (confidence: {info.language_probability:.2f})")
        
        segments = []
        full_text = ""

        if detected_lang in ["hi", "ur", "ne", "mr"]:
            from transliterate import hindi_to_hinglish

            # ── FIX 4: Urdu outputs Arabic script — re-transcribe as Hindi ────
            # Whisper often confuses Hindi & Urdu (phonetically similar).
            # Urdu output is Arabic script; our transliterator only handles
            # Devanagari. Force re-transcribe as Hindi to get Devanagari.
            if detected_lang == "ur":
                print("Urdu detected — re-transcribing as Hindi (Devanagari) for Hinglish conversion...")
                hi_prompt = "यह एक साधारण हिंदी बातचीत है। इसमें गालियां और अपशब्द भी हो सकते हैं।"
                segments_gen, _ = model.transcribe(
                    temp_path,
                    language="hi",
                    initial_prompt=hi_prompt,
                    condition_on_previous_text=False,
                    temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                    no_speech_threshold=0.6,
                    vad_filter=False,
                    beam_size=5,
                )

            for segment in segments_gen:
                raw = segment.text.strip()
                print(f"  [{segment.start:.1f}s] {raw[:40]}")
                segments.append({"start": segment.start, "end": segment.end, "text": raw})
                full_text += raw + " "

        else:
            print(f"Language '{detected_lang}' detected — translating to English...")
            segments_gen_en, _ = model.transcribe(
                temp_path,
                language=detected_lang,
                initial_prompt="Hello, how are you? I am speaking. Okay, that is fine. Thank you so much.",
                condition_on_previous_text=False,
                temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                no_speech_threshold=0.6,
                vad_filter=False,   # ← same fix
                beam_size=5,
                task="translate"
            )
            for segment in segments_gen_en:
                t = segment.text.strip()
                print(f"  [{segment.start:.1f}s] {t[:50]}")
                segments.append({"start": segment.start, "end": segment.end, "text": t})
                full_text += t + " "

        full_text = full_text.strip()
        print(f"Transcription complete: {len(full_text)} chars, {len(segments)} segments")

        # ── Warn clearly if output is still empty ────────────────────────────
        if not full_text:
            print("WARNING: Whisper produced no output. Audio may be silent, too short, or corrupt.")
            return {
                "success": False,
                "error": f"Whisper could not detect speech in this audio (detected lang: {detected_lang}, prob: {info.language_probability:.2f}). "
                          "Try a different audio file or check if the recording has actual speech."
            }

        # Diarization
        turns = []
        try:
            print("Running Speaker Diarization...", flush=True)
            print("Starting fast_diarize...", flush=True)
            turns = fast_diarize(temp_path, segments)
            print("Finished fast_diarize successfully!", flush=True)
        except Exception as e:
            print(f"Diarization error: {e}")
            turns = [{"speaker": "agent", "text": full_text, "time": "0:00"}]

        # ── Gemini Transliteration for Hindi / Regional Languages ──
        gemini_success = False
        if detected_lang in ["hi", "ur", "ne", "mr"] and client and turns:
            try:
                print("Running Gemini transliteration for app.py transcribe...")
                prompt = f"""
Analyze this call transcript where the text is in Devanagari script (Hindi/Marathi/etc.).
For each turn, you must:
1. Transliterate the "text" field into clean, modern, natural Roman Hinglish (e.g. convert "लड़की" to "ladki", "व्हाट्सएप" to "whatsapp", "स्कैनर" to "scanner", "प्रॉब्लम" to "problem"). Do NOT use academic dot notation (like la.daka or vatasaba).
2. Translate the "text" field into professional English and put it in a new field called "english".
Return ONLY a valid JSON array of objects with exactly "speaker", "time", "text" (for Roman Hinglish), and "english" (for English translation) fields. Do not include markdown blocks like ```json.
Transcript:
{json.dumps(turns)}
"""
                resp_text = call_gemini(prompt)
                if resp_text.startswith("```json"):
                    resp_text = resp_text[7:]
                if resp_text.startswith("```"):
                    resp_text = resp_text[3:]
                if resp_text.endswith("```"):
                    resp_text = resp_text[:-3]
                
                translated_turns = json.loads(resp_text.strip())
                if isinstance(translated_turns, list):
                    turns = translated_turns
                    gemini_success = True
                    # Reconstruct full_text in Hinglish
                    full_text = " ".join([t.get("text", "") for t in turns]).strip()
            except Exception as e:
                print("Gemini transliteration failed in app.py, falling back to rule-based:", e)

        if detected_lang in ["hi", "ur", "ne", "mr"] and not gemini_success:
            # Fallback to rule-based transliteration
            from transliterate import hindi_to_hinglish
            for turn in turns:
                turn["text"] = hindi_to_hinglish(turn.get("text", ""))
                turn["english"] = turn["text"]
            full_text = " ".join([t.get("text", "") for t in turns]).strip()

        return {
            "success": True,
            "text": full_text,
            "segments": segments,
            "language": detected_lang,
            "turns": turns
        }

    except Exception as e:
        import traceback
        print(f"Transcription error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

import urllib.request
from analyzer import analyze_text
import re
from deep_translator import GoogleTranslator
from transliterate import hindi_to_hinglish
from gender_detector import detect_speaker_gender
from pitch_diarize import pitch_diarize
from emailer import send_violation_alert_email

def load_bad_words():
    bad_words_path = os.path.join(os.path.dirname(__file__), "bad_words.txt")
    if not os.path.exists(bad_words_path):
        return []
    with open(bad_words_path, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

BAD_WORDS_LIST = load_bad_words()

def check_for_violations(turns):
    incidents = []
    for turn in turns:
        text = turn.get("text", "").lower()
        violations_found = []
        for bw in BAD_WORDS_LIST:
            # simple substring or word boundary match
            import re
            if re.search(r'\b' + re.escape(bw) + r'\b', text):
                violations_found.append(bw)
        
        if violations_found:
            incidents.append({
                "time": turn.get("time", "0:00"),
                "speaker": turn.get("speaker", "Unknown"),
                "text": turn.get("text", ""),
                "violations": list(set(violations_found))
            })
    return incidents

def process_mixed_text(text: str) -> str:
    # 1. Translate South Indian/Other scripts to English
    non_hindi_indic = r'[\u0D00-\u0D7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0980-\u09FF\u0A80-\u0AFF\u0A00-\u0A7F\u0B00-\u0B7F]'
    if re.search(non_hindi_indic, text):
        try:
            text = GoogleTranslator(source='auto', target='en').translate(text)
        except:
            pass
            
    # 2. Transliterate Hindi (Devanagari) to Hinglish
    devanagari = r'[\u0900-\u097F]'
    if re.search(devanagari, text):
        hinglish = hindi_to_hinglish(text)
        text = hinglish if hinglish else text
        
    return text.strip()

@app.post("/api/analyze-call")
async def analyze_call(request: Request):
    try:
        content_type = request.headers.get('content-type', '')
        if 'application/json' in content_type:
            data = await request.json()
        else:
            data = await request.form()
            
        adviser_id = data.get("reciever_ref_code") or data.get("adviser_id")
        user_id = data.get("sender_ref_code") or data.get("user_id")
        voice_url = data.get("voice_url")
        
        if not voice_url:
            raise HTTPException(status_code=400, detail="voice_url is required")

        print(f"Webhook Received: adviser={adviser_id}, user={user_id}, url={voice_url}")
        
        payload = _run_heavy_analysis(
            adviser_id,
            user_id,
            voice_url
        )
        
        if payload.get("success") and "transcript" in payload:
            incidents = check_for_violations(payload["transcript"])
            if incidents:
                print(f"🚨 Violations found! Sending email alert...")
                all_violations = []
                for inc in incidents:
                    all_violations.extend(inc["violations"])
                
                alert_data = {
                    "user_id": user_id,
                    "adviser_id": adviser_id,
                    "violations": list(set(all_violations)),
                    "incidents": incidents,
                    "transcript": payload.get("full_text", ""),
                    "audio_url": voice_url
                }
                
                import threading
                threading.Thread(target=send_violation_alert_email, args=(alert_data,)).start()
            else:
                print("✅ Voice is normal. No bad words used. Ignoring & moving to next.")
                
            # Add incidents to payload so frontend can see it during testing
            payload["incidents"] = incidents
            
        if not payload.get("success"):
            raise HTTPException(status_code=500, detail=payload.get("error", "Unknown backend error"))
            
        return payload

    except Exception as e:
        print(f"Error in analyze-call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

import threading
import subprocess
import sys
analysis_lock = threading.Lock()

def _run_heavy_analysis(adviser_id: str, user_id: str, voice_url: str) -> dict:
    with analysis_lock:
        print(f"Spawning worker for {voice_url}")
        try:
            import os
            worker_path = os.path.join(os.path.dirname(__file__), "worker.py")
            proc = subprocess.run(
                [sys.executable, worker_path, adviser_id, user_id, voice_url],
                capture_output=True,
                text=True,
                encoding='utf-8' # Handle Hinglish/Hindi characters properly
            )
            for line in proc.stdout.splitlines():
                if line.startswith("WORKER_RESULT:"):
                    return json.loads(line.replace("WORKER_RESULT:", "", 1))
            return {"success": False, "error": f"Worker failed. Stderr: {proc.stderr[-500:]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def _run_heavy_analysis_internal(adviser_id: str, user_id: str, voice_url: str) -> dict:
    try:
        # 1. Download audio file
        ext = voice_url.rsplit(".", 1)[-1].lower() if "." in voice_url else "mp3"
        # Handle cases where url might have query params like .webm?alt=media
        ext = ext.split("?")[0]
        allowed_exts = {"mp3", "wav", "webm", "m4a", "ogg", "flac", "mp4", "aac"}
        if ext not in allowed_exts:
            ext = "mp3"
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
            req = urllib.request.Request(voice_url, headers={'User-Agent': 'Mozilla/5.0'})
            import shutil
            with urllib.request.urlopen(req, timeout=30) as response:
                shutil.copyfileobj(response, temp_audio)
            temp_path = temp_audio.name
            
        print("Audio downloaded, starting Whisper transcription...")
        
        # 2. Transcribe and Process
        # We transcribe in the native scripts, then post-process:
        # Hindi -> Hinglish, Malayalam -> English
        transcribe_options = dict(
            condition_on_previous_text=False, # Disable to prevent infinite repetition loops on CPU
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], # Enable fallback to escape loops
            no_speech_threshold=0.6,          # Drop silent segments that cause loops
            word_timestamps=False,
            beam_size=5,                      # Maximize accuracy with beam search
            initial_prompt="हाँ, ठीक है, जी, अच्छा।" # Prime model for accurate Hindi/English
        )
        
        segments_gen, info = model.transcribe(temp_path, language=None, **transcribe_options)
        
        # Whisper often confuses Hindi and Urdu due to phonetic similarity.
        # If it detects Urdu, it outputs Arabic script. We force Hindi to get Devanagari,
        # which our Hinglish transliterator handles perfectly.
        if info.language == "ur":
            print("Detected Urdu. Re-transcribing as Hindi to enforce Devanagari script for Hinglish conversion...")
            hi_prompt = "यह एक साधारण हिंदी बातचीत है। इसमें गालियां और अपशब्द भी हो सकते हैं।"
            segments_gen, info = model.transcribe(temp_path, language="hi", initial_prompt=hi_prompt, **transcribe_options)
        elif info.language not in ["hi", "en"]:
            print(f"Detected {info.language}. Re-transcribing natively to English using Whisper's translate task for maximum accuracy...")
            # Whisper's native translation translates acoustic context, preserving exact meaning much better than text translators.
            segments_gen, info = model.transcribe(temp_path, task="translate", **transcribe_options)
            
        detected_lang = info.language
        print(f"Primary audio language detected: {detected_lang}. Running mixed-language translation...")
        
        full_text = ""
        whisper_segments = []
        
        for segment in segments_gen:
            processed_full_text = process_mixed_text(segment.text.strip())
            full_text += processed_full_text + " "
            if getattr(segment, 'words', None):
                current_chunk = {"start": segment.words[0].start, "end": segment.words[0].end, "text": ""}
                for w in segment.words:
                    if w.start - current_chunk["start"] > 1.5: # evaluate pitch every 1.5s
                        current_chunk["text"] = process_mixed_text(current_chunk["text"])
                        whisper_segments.append(current_chunk)
                        current_chunk = {"start": w.start, "end": w.end, "text": w.word.strip()}
                    else:
                        current_chunk["end"] = w.end
                        current_chunk["text"] += " " + w.word.strip()
                if current_chunk["text"].strip():
                    current_chunk["text"] = process_mixed_text(current_chunk["text"])
                    whisper_segments.append(current_chunk)
            else:
                whisper_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": processed_full_text
                })
                
        full_text = full_text.strip()
        print(f"Transcription complete: {full_text[:50]}...")
        
        # 2.5 Lightning-Fast Diarization & Metrics
        metrics = {
            "agent_talk_time": 0,
            "customer_talk_time": 0,
            "silence_time": 0,
            "total_time": whisper_segments[-1]["end"] if whisper_segments else 0
        }
        
        try:
            print("Running pitch-based speaker diarization...")
            turns = pitch_diarize(temp_path, whisper_segments)
            
            # Calculate metrics
            for turn in turns:
                duration = turn["end_time"] - turn["start_time"]
                if turn["speaker"] == "agent":
                    metrics["agent_talk_time"] += duration
                else:
                    metrics["customer_talk_time"] += duration
                    
        except Exception as e:
            print(f"Diarization error: {e} — using single-speaker fallback")
            turns = [{"speaker": "agent", "text": full_text, "time": "0:00"}]
            metrics["agent_talk_time"] = metrics["total_time"]
            
        metrics["silence_time"] = max(0, metrics["total_time"] - metrics["agent_talk_time"] - metrics["customer_talk_time"])            
        os.remove(temp_path)
        
        # 3. Analyze
        analysis_result = analyze_text(full_text)
        
        # 3.2 Detailed Incident Analysis per Turn
        incidents = []
        for turn in turns:
            res = analyze_text(turn["text"])
            turn_flags = res.get("flags", {})
            if turn_flags.get("abuse_detected") or turn_flags.get("phone_shared") or turn_flags.get("threat_detected"):
                vlist = []
                if turn_flags.get("abuse_detected"): vlist.append("Abusive Language")
                if turn_flags.get("phone_shared"): vlist.append("Phone Number / PII Sharing")
                if turn_flags.get("threat_detected"): vlist.append("Threat")
                
                incidents.append({
                    "time": turn["time"],
                    "speaker": turn["speaker"].capitalize(),
                    "text": turn["text"],
                    "violations": vlist
                })
        
        # 3.5 Check for alerts
        flags = analysis_result.get("flags", {})
        if flags.get("abuse_detected") or flags.get("phone_shared"):
            violations = []
            if flags.get("abuse_detected"):
                violations.append("Abusive Language")
            if flags.get("phone_shared"):
                violations.append("Phone Number / PII Sharing")
                
            alert_data = {
                "user_id": user_id,
                "adviser_id": adviser_id,
                "violations": violations,
                "incidents": incidents,
                "transcript": full_text,
                "audio_url": voice_url
            }
            
            # Fire and forget email alerts
            from emailer import send_violation_alert_email
            import threading
            
            threading.Thread(target=send_violation_alert_email, args=(alert_data,)).start()
        
        # 4. Construct n8n payload
        payload = {
            "success": True,
            "reciever_ref_code": adviser_id,
            "sender_ref_code": user_id,
            "adviser_id": adviser_id,
            "user_id": user_id,
            "voice_url": voice_url,
            "transcript": full_text,
            "language": detected_lang,
            "metrics": metrics,
            "analysis": analysis_result,
            "incidents": incidents,
            "turns": turns
        }
        
        return payload
        
    except Exception as e:
        print(f"Error in analyze-call: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/batch-analyze")
async def batch_analyze(request: Request):
    """
    Accepts a JSON payload with an array of calls:
    {
      "calls": [
        {
          "user_id": "USR-1",
          "adviser_id": "ADV-1",
          "transcript": "Hello"
        }
      ]
    }
    """
    try:
        data = await request.json()
        calls = data.get("calls", [])
        if not isinstance(calls, list):
            return {"success": False, "error": "'calls' must be an array"}
            
        results = []
        for index, call in enumerate(calls):
            user_id = call.get("sender_ref_code") or call.get("user_id", "Unknown")
            adviser_id = call.get("reciever_ref_code") or call.get("adviser_id", "Unknown")
            transcript = call.get("transcript", "")
            
            if not transcript.strip():
                results.append({
                    "index": index,
                    "reciever_ref_code": adviser_id,
                    "sender_ref_code": user_id,
                    "user_id": user_id,
                    "adviser_id": adviser_id,
                    "error": "Empty transcript"
                })
                continue
                
            analysis_result = analyze_text(transcript)
            
            results.append({
                "index": index,
                "reciever_ref_code": adviser_id,
                "sender_ref_code": user_id,
                "user_id": user_id,
                "adviser_id": adviser_id,
                "transcript": transcript,
                "analysis": analysis_result
            })
            
        return {
            "success": True,
            "total_processed": len(results),
            "data": results
        }
    except Exception as e:
        print(f"Error in batch-analyze: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
