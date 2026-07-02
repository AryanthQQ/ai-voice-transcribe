import torch
import librosa
from pyannote.audio import Pipeline
import os

HF_TOKEN = os.getenv("HF_TOKEN")
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN)

temp_path = r"C:\Users\hp\AppData\Local\Temp\tmpbm3w7g5w.mp3"
y, sr = librosa.load(temp_path, sr=16000)
waveform = torch.from_numpy(y).unsqueeze(0)

try:
    diarization = diarization_pipeline({"waveform": waveform, "sample_rate": sr})
    print("Pyannote succeeded!")
except Exception as e:
    print(f"Pyannote failed: {e}")
