import librosa
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def pitch_diarize(audio_path: str, whisper_segments: list) -> list:
    """
    Lightning-fast diarization based on relative pitch!
    Agent = Female (Higher Relative Pitch)
    Customer = Male (Lower Relative Pitch)
    """
    print("Running Dynamic Pitch Diarization...")
    y, sr = librosa.load(audio_path, sr=16000)
    
    # First pass: collect valid median pitches for all segments
    segment_pitches = []
    for seg in whisper_segments:
        start_sample = int(seg["start"] * sr)
        end_sample = int(seg["end"] * sr)
        chunk = y[start_sample:end_sample]
        
        if len(chunk) < sr * 0.3:
            segment_pitches.append(None)
        else:
            f0, voiced_flag, _ = librosa.pyin(y=chunk, sr=sr, fmin=50, fmax=400)
            f0 = f0[voiced_flag]
            if len(f0) > 0:
                segment_pitches.append(np.median(f0))
            else:
                segment_pitches.append(None)
                
    # Determine the threshold using 1D K-Means clustering to find the two speakers
    valid_pitches = [p for p in segment_pitches if p is not None]
    if len(valid_pitches) >= 2:
        c1, c2 = min(valid_pitches), max(valid_pitches)
        for _ in range(10): # 10 iterations of K-Means
            g1 = [p for p in valid_pitches if abs(p - c1) < abs(p - c2)]
            g2 = [p for p in valid_pitches if abs(p - c1) >= abs(p - c2)]
            c1 = float(np.mean(g1)) if g1 else c1
            c2 = float(np.mean(g2)) if g2 else c2
        pitch_threshold = (c1 + c2) / 2
    else:
        pitch_threshold = 160 # fallback

    turns = []
    for i, seg in enumerate(whisper_segments):
        pitch = segment_pitches[i]
        
        if pitch is not None:
            # Female Agent = Higher pitch than the threshold
            # Male Customer = Lower pitch than the threshold
            if pitch > pitch_threshold:
                speaker = "agent"
            else:
                speaker = "customer"
        else:
            speaker = "unknown"
            
        # Resolve unknown based on previous speaker or default to agent
        if speaker == "unknown":
            speaker = turns[-1]["speaker"] if turns else "agent"
            
        mins = int(seg["start"] // 60)
        secs = int(seg["start"] % 60)
        
        if turns and turns[-1]["speaker"] == speaker:
            turns[-1]["text"] += " " + seg["text"]
            turns[-1]["end_time"] = seg["end"]
        else:
            turns.append({
                "speaker": speaker,
                "text": seg["text"],
                "time": f"{mins}:{secs:02d}",
                "start_time": seg["start"],
                "end_time": seg["end"]
            })
            
    return turns
