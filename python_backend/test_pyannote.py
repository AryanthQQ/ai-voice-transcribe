import torch
from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
token = os.environ.get("HF_TOKEN")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=token)
tensor = torch.randn(1, 16000)
out = pipeline({"waveform": tensor, "sample_rate": 16000})
print(dir(out))
print(out)
