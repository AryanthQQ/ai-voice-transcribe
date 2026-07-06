import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "2"   # keep it low to avoid OpenMP conflicts

import sys
import json
import urllib.request
import tempfile
import shutil
import numpy as np

from faster_whisper import WhisperModel
import librosa
from sklearn.cluster import KMeans
from transliterate import hindi_to_hinglish
from dotenv import load_dotenv
from pyannote.audio import Pipeline


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
        print("[GEMINI] genai client initialized successfully in worker.py!")
    except Exception as e:
        print("[GEMINI] Failed to initialize genai client in worker.py:", e)

def call_gemini(prompt: str, model="gemini-2.5-flash-lite") -> str:
    if not client:
        raise ValueError("Gemini client not initialized")
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text.strip()


def get_pitch_simple(y, sr):
    """
    Lightweight pitch estimation using librosa piptrack.
    Returns mean pitch in Hz. Higher = female (Agent), Lower = male (Customer).
    """
    try:
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
        # Select pitch at highest magnitude per frame
        pitch_values = []
        for t in range(pitches.shape[1]):
            mag_col = magnitudes[:, t]
            idx = mag_col.argmax()
            if magnitudes[idx, t] > 0:
                p = pitches[idx, t]
                if 80 < p < 500:   # human voice range
                    pitch_values.append(p)
        if not pitch_values:
            return 0.0
        return float(np.mean(pitch_values))
    except Exception:
        return 0.0


def run(adviser_id, user_id, voice_url):
    try:
        # ── 0. Initialize Vertex AI (Gemini) ───────────────────────────────
        gemini_model = None
        gcp_cred_path = os.path.join(os.path.dirname(__file__), "gcp-credentials.json")
        if os.path.exists(gcp_cred_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_cred_path
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                with open(gcp_cred_path, "r") as f:
                    cred_data = json.load(f)
                    project_id = cred_data.get("project_id", "ai-modal-492711")
                vertexai.init(project=project_id, location="us-central1")
                gemini_model = GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                print("Failed to init Vertex AI:", e)
        # ── 1. Load Model ──────────────────────────────────────────────────
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        load_dotenv()
        hf_token = os.getenv("HF_TOKEN")
        
        model = WhisperModel(
            "large-v3",
            device=device,
            compute_type=compute_type,
            cpu_threads=4 if device == "cpu" else 0,
            num_workers=1
        )

        # ── 2. Download Audio ──────────────────────────────────────────────
        temp_path = None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            req = urllib.request.Request(voice_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                shutil.copyfileobj(resp, tmp)
            temp_path = tmp.name

        # ── 3. Transcribe (No Translation) to preserve original words ──────
        segments_gen, info = model.transcribe(
            temp_path,
            beam_size=5,
            task="transcribe",
            language="hi",                # Force Hindi script (perfect for Marathi/Hindi, outputs Devanagari)
            vad_filter=True,              # Silero VAD removes silences to prevent hallucinations
            vad_parameters=dict(min_silence_duration_ms=500),
            condition_on_previous_text=False, # Must be False for large-v3 to prevent loops
            no_repeat_ngram_size=2,       # Stricter repeat block
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
            temperature=0.0,
        )

        whisper_segments = []
        full_text = ""
        for seg in segments_gen:
            t = seg.text.strip()
            if not t:
                continue
                
            # Keep raw Devanagari (Hindi/Urdu/Marathi text as Devanagari script)
            # Transliteration will be handled by Gemini (or fallback) at the end.
            
            whisper_segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": t,
                "no_speech_prob": seg.no_speech_prob
            })
            full_text += t + " "

        full_text = full_text.strip()

        if not full_text or len(whisper_segments) == 0:
            result = {"success": False, "error": "No speech detected in audio"}
            print("WORKER_RESULT:" + json.dumps(result))
            return

        # ── 4. Load audio for pitch processing ────────────────────────────
        y, sr = librosa.load(temp_path, sr=16000, mono=True)

        # ── 5. Pyannote Diarization ───────────────────────────────────────
        diarization_pipeline = None
        if hf_token:
            try:
                diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=hf_token
                )
                if device == "cuda":
                    diarization_pipeline.to(torch.device("cuda"))
            except Exception as e:
                print("Failed to load Pyannote:", str(e))

        if diarization_pipeline:
            diarization = diarization_pipeline(temp_path)
            pyannote_segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                pyannote_segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })

            # Figure out pitch for each speaker to map Agent vs Customer
            speaker_pitches = {}
            for p_seg in pyannote_segments:
                s = int(p_seg['start'] * sr)
                e = int(p_seg['end'] * sr)
                chunk = y[s:e]
                if len(chunk) > sr * 0.1:
                    pitch = get_pitch_simple(chunk, sr)
                    if pitch > 0:
                        spk = p_seg['speaker']
                        speaker_pitches.setdefault(spk, []).append(pitch)

            # Calculate avg pitch per speaker
            avg_pitch = {}
            for spk, pitches in speaker_pitches.items():
                avg_pitch[spk] = float(np.mean(pitches))

            # Map Agent and Customer
            if len(avg_pitch) >= 2:
                # sort by pitch descending
                sorted_speakers = sorted(avg_pitch.keys(), key=lambda k: avg_pitch[k], reverse=True)
                cluster_to_role = {sorted_speakers[0]: "Agent", sorted_speakers[1]: "Customer"}
                for spk in sorted_speakers[2:]:
                    cluster_to_role[spk] = "Unknown"
            elif len(avg_pitch) == 1:
                spk = list(avg_pitch.keys())[0]
                cluster_to_role = {spk: "Agent" if avg_pitch[spk] > 160 else "Customer"}
            else:
                cluster_to_role = {}

            # Map whisper segments to pyannote speakers
            turns = []
            for w_seg in whisper_segments:
                w_mid = (w_seg['start'] + w_seg['end']) / 2
                
                best_speaker = "Unknown"
                for p_seg in pyannote_segments:
                    if p_seg['start'] <= w_mid <= p_seg['end']:
                        best_speaker = cluster_to_role.get(p_seg['speaker'], p_seg['speaker'])
                        break
                
                if best_speaker == "Unknown":
                    # Fallback to nearest
                    nearest_speaker = None
                    min_dist = float('inf')
                    for p_seg in pyannote_segments:
                        dist = min(abs(w_mid - p_seg['start']), abs(w_mid - p_seg['end']))
                        if dist < min_dist:
                            min_dist = dist
                            nearest_speaker = p_seg['speaker']
                    if nearest_speaker:
                        best_speaker = cluster_to_role.get(nearest_speaker, nearest_speaker)

                mins = int(w_seg["start"] // 60)
                secs = int(w_seg["start"] % 60)
                
                if turns and turns[-1]["speaker"] == best_speaker:
                    turns[-1]["text"] += " " + w_seg["text"]
                else:
                    turns.append({
                        "speaker": best_speaker,
                        "text": w_seg["text"],
                        "time": f"{mins}:{secs:02d}"
                    })
        else:
            # --- FALLBACK: K-Means Diarization if Pyannote fails ---
            mfcc_features = []
            pitch_per_segment = []

            for seg in whisper_segments:
                s = int(seg['start'] * sr)
                e = int(seg['end'] * sr)
                chunk = y[s:e]

                if len(chunk) < sr * 0.1:
                    mfcc_features.append(np.zeros(13))
                    pitch_per_segment.append(0.0)
                    continue

                mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
                mfcc_features.append(np.mean(mfcc, axis=1))
                pitch_per_segment.append(get_pitch_simple(chunk, sr))

            X = np.array(mfcc_features)

            if len(whisper_segments) == 1:
                labels = [0]
            else:
                n_clusters = min(2, len(whisper_segments))
                kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=0)
                labels = kmeans.fit_predict(X).tolist()

            cluster_pitches = {0: [], 1: []}
            for i, lbl in enumerate(labels):
                p = pitch_per_segment[i]
                if p > 0:
                    cluster_pitches[lbl].append(p)

            avg0 = float(np.mean(cluster_pitches[0])) if cluster_pitches[0] else 0.0
            avg1 = float(np.mean(cluster_pitches[1])) if cluster_pitches[1] else 0.0

            if avg0 >= avg1:
                cluster_to_role = {0: "Agent", 1: "Customer"}
            else:
                cluster_to_role = {0: "Customer", 1: "Agent"}

            turns = []
            for i, seg in enumerate(whisper_segments):
                speaker = cluster_to_role.get(labels[i], "Agent")
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

        # ── 9. Gemini Translation & Summary ──────────────────────
        summary_text = ""
        gemini_success = False
        if client and turns:
            try:
                # Prompt Gemini to convert Devanagari to BOTH natural Roman Hinglish and English translation
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
                    
                # Generate summary
                summary_prompt = f"Summarize this call in 2-3 sentences based on the following transcript:\n{json.dumps(turns)}"
                summary_text = call_gemini(summary_prompt)
            except Exception as e:
                print("Gemini processing failed, falling back to rule-based transliteration:", e)

        # Fallback to rule-based transliteration if Gemini is not available or failed
        if not gemini_success:
            for turn in turns:
                turn["text"] = hindi_to_hinglish(turn.get("text", ""))
                turn["english"] = turn["text"]  # Simple fallback
            full_text = " ".join([t.get("text", "") for t in turns]).strip()

        # ── 10. Output result ───────────────────────────────────────────────
        result = {
            "success": True,
            "transcript": turns,
            "full_text": full_text,
            "language": info.language,
            "summary": summary_text
        }
        print("WORKER_RESULT:" + json.dumps(result))

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print("WORKER_RESULT:" + json.dumps({
            "success": False,
            "error": str(e),
            "trace": err
        }))
    finally:
        try:
            if temp_path:
                os.remove(temp_path)
        except Exception:
            pass


if __name__ == "__main__":
    if len(sys.argv) == 4:
        run(sys.argv[1], sys.argv[2], sys.argv[3])
