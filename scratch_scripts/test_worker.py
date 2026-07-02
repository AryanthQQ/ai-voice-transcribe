import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "4"
import json
import urllib.request
import tempfile
import shutil
import sys

print("Loading model...", flush=True)
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="default")
print("Model loaded.", flush=True)

def run():
    url = "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_78154535_62551043_345637900926/rec_audio_call_78154535_62551043_345637900926_audio_1782196256613.mp3"
    print("Downloading audio...", flush=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            shutil.copyfileobj(response, temp_audio)
        temp_path = temp_audio.name
    print(f"Downloaded to {temp_path}", flush=True)

    print("Transcribing...", flush=True)
    segments_gen_en, info = model.transcribe(
        temp_path,
        beam_size=5,
        task="translate"
    )
    segments = []
    full_text = ""
    for segment in segments_gen_en:
        t = segment.text.strip()
        print(f"  [{segment.start:.1f}s] {t[:50]}", flush=True)
        segments.append({"start": segment.start, "end": segment.end, "text": t})
        full_text += t + " "

    print(f"Transcription complete: {len(full_text)} chars", flush=True)

    print("Running librosa.load...", flush=True)
    import librosa
    y, sr = librosa.load(temp_path, sr=16000)
    
    print("Running MFCC...", flush=True)
    import numpy as np
    features = []
    for seg in segments:
        start_sample = int(seg['start'] * sr)
        end_sample = int(seg['end'] * sr)
        chunk = y[start_sample:end_sample]
        if len(chunk) == 0:
            features.append(np.zeros(13))
            continue
        mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
        features.append(np.mean(mfcc, axis=1))
    X = np.array(features)
    
    print("Running KMeans...", flush=True)
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, n_init=10, random_state=0)
    labels = kmeans.fit_predict(X)
    print("DONE!!!", flush=True)

run()
