import sys
from faster_whisper import WhisperModel
import urllib.request
import tempfile
import os

print("Downloading file...")
voice_url = 'https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_85133471_35297953_46795036ae2b/rec_audio_call_85133471_35297953_46795036ae2b_audio_1782196082989.mp3'
with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
    req = urllib.request.Request(voice_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        temp_audio.write(response.read())
    temp_path = temp_audio.name

print("File downloaded to:", temp_path)
print("Loading model...")
model = WhisperModel("medium", device="cpu", compute_type="float32")
print("Model loaded. Transcribing...")
try:
    segments, info = model.transcribe(temp_path, language="hi")
    print("Transcription started, language:", info.language)
    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s]: {segment.text}")
    print("Transcription finished successfully!")
except Exception as e:
    print("Error during transcription:", e)
finally:
    if os.path.exists(temp_path):
        os.remove(temp_path)
