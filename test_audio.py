import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "python_backend"))
from app import _run_heavy_analysis

url = "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_62815017_24874032_b624e6ff6f96/rec_audio_call_62815017_24874032_b624e6ff6f96_audio_1782502095594.mp3"
result = _run_heavy_analysis("test_adv", "test_usr", url)
print("SUCCESS!" if result.get('success') else f"FAILED: {result.get('error')}")
