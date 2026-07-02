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
        # ── 1. Load Model ──────────────────────────────────────────────────
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
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
                
            # Convert Devanagari to Roman (Hinglish/Marathi in English script)
            t = hindi_to_hinglish(t)
            
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

        # ── 4. Load audio for diarization ─────────────────────────────────
        y, sr = librosa.load(temp_path, sr=16000, mono=True)

        # ── 5. Feature extraction: MFCC + pitch per segment ────────────────
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

        # ── 6. K-Means Diarization ─────────────────────────────────────────
        if len(whisper_segments) == 1:
            labels = [0]
        else:
            n_clusters = min(2, len(whisper_segments))
            kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=0)
            labels = kmeans.fit_predict(X).tolist()

        # ── 7. Map clusters → Agent / Customer using pitch ─────────────────
        cluster_pitches = {0: [], 1: []}
        for i, lbl in enumerate(labels):
            p = pitch_per_segment[i]
            if p > 0:
                cluster_pitches[lbl].append(p)

        avg0 = float(np.mean(cluster_pitches[0])) if cluster_pitches[0] else 0.0
        avg1 = float(np.mean(cluster_pitches[1])) if cluster_pitches[1] else 0.0

        # Higher pitch = Agent (female), lower = Customer (male)
        if avg0 >= avg1:
            cluster_to_role = {0: "Agent", 1: "Customer"}
        else:
            cluster_to_role = {0: "Customer", 1: "Agent"}

        # ── 8. Build conversation turns ───────────────────────────────────
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

        # ── 9. Output result ───────────────────────────────────────────────
        result = {
            "success": True,
            "transcript": turns,
            "full_text": full_text,
            "language": info.language,
            "summary": ""
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
