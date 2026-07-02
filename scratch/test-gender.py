import librosa
import numpy as np
import urllib.request
import tempfile
import sys
import warnings

warnings.filterwarnings('ignore')

def detect_gender(audio_path, offset, duration):
    try:
        # Load a small snippet of audio
        y, sr = librosa.load(audio_path, sr=16000, offset=offset, duration=duration)
        
        # Extract fundamental frequency (f0) using pyin
        # typical human vocal range: 50 Hz to 300 Hz
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=300, sr=sr)
        
        # Filter out NaN values (unvoiced frames)
        f0 = f0[voiced_flag]
        
        if len(f0) == 0:
            return "Unknown", 0.0
            
        median_pitch = np.median(f0)
        
        # Threshold: > 160 Hz is generally female, < 160 is male
        gender = "Female" if median_pitch > 160 else "Male"
        
        return gender, float(median_pitch)
    except Exception as e:
        print(f"Error detecting gender: {e}")
        return "Unknown", 0.0

if __name__ == "__main__":
    print("Downloading audio...")
    voice_url = "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_85133471_35297953_46795036ae2b/rec_audio_call_85133471_35297953_46795036ae2b_audio_1782196082989.mp3"
    req = urllib.request.Request(voice_url, headers={'User-Agent': 'Mozilla/5.0'})
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        with urllib.request.urlopen(req) as response:
            temp_audio.write(response.read())
        temp_path = temp_audio.name
        
    print(f"Audio downloaded to {temp_path}")
    
    # We know from the transcript:
    # Speaker 1 (agent) starts at 0:02 ("hello hello"). Let's check 2.0 to 4.0
    g1, p1 = detect_gender(temp_path, offset=2.0, duration=2.0)
    print(f"Segment 1 (Agent, 2s-4s): {g1}, Pitch: {p1:.1f} Hz")
    
    # Speaker 2 (customer) starts at 0:08 ("hello"). Let's check 8.0 to 12.0
    g2, p2 = detect_gender(temp_path, offset=8.0, duration=4.0)
    print(f"Segment 2 (Customer, 8s-12s): {g2}, Pitch: {p2:.1f} Hz")
    
    # Another customer segment at 30s ("dil todkar hasatee hai mera")
    g3, p3 = detect_gender(temp_path, offset=30.0, duration=4.0)
    print(f"Segment 3 (Customer, 30s-34s): {g3}, Pitch: {p3:.1f} Hz")
