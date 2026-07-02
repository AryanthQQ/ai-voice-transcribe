import sys
import os
import urllib.request
import tempfile
import shutil
import time

url = "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_62815017_24874032_b624e6ff6f96/rec_audio_call_62815017_24874032_b624e6ff6f96_audio_1782502095594.mp3"

print("Downloading...", flush=True)
ext = "mp3"
with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        shutil.copyfileobj(response, temp_audio)
    temp_path = temp_audio.name

print(f"Downloaded to {temp_path}", flush=True)

from faster_whisper import WhisperModel
print("Loading model...", flush=True)
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
print("Model loaded!", flush=True)

start = time.time()
print("Starting transcribe...", flush=True)
segments_gen, info = model.transcribe(temp_path, language=None)
print(f"Detected {info.language}", flush=True)
for segment in segments_gen:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}", flush=True)
    
print(f"Finished in {time.time() - start:.2f}s", flush=True)
