import librosa
import numpy as np
import warnings

warnings.filterwarnings('ignore')

def detect_speaker_gender(audio_path: str, diarization) -> dict:
    """
    Given an audio file and a pyannote diarization result, 
    detect the gender of each speaker by sampling their speech.
    Returns a mapping: { 'SPEAKER_00': 'agent', 'SPEAKER_01': 'customer' }
    Assume Female (Pitch > 160Hz) = agent, Male (Pitch <= 160Hz) = customer
    """
    try:
        # Group segments by speaker
        speaker_segments = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if speaker not in speaker_segments:
                speaker_segments[speaker] = []
            speaker_segments[speaker].append((turn.start, turn.end))
            
        speaker_mapping = {}
        for speaker, segments in speaker_segments.items():
            # Sort by length and take the 3 longest segments to sample
            segments.sort(key=lambda x: x[1] - x[0], reverse=True)
            samples = segments[:3]
            
            pitches = []
            for start, end in samples:
                duration = min(end - start, 3.0) # max 3 seconds per sample
                if duration < 0.5:
                    continue # too short
                    
                y, sr = librosa.load(audio_path, sr=16000, offset=start, duration=duration)
                f0, voiced_flag, _ = librosa.pyin(y, fmin=50, fmax=300, sr=sr)
                f0 = f0[voiced_flag]
                if len(f0) > 0:
                    pitches.append(np.median(f0))
                    
            if pitches:
                median_pitch = np.median(pitches)
                print(f"[{speaker}] Median Pitch: {median_pitch:.1f} Hz")
                if median_pitch > 160:
                    speaker_mapping[speaker] = "agent"
                else:
                    speaker_mapping[speaker] = "customer"
            else:
                # Fallback if pitch detection fails
                print(f"[{speaker}] Pitch detection failed, using fallback")
                speaker_mapping[speaker] = "unknown"
                
        # Resolve conflicts if both are 'agent' or both are 'customer'
        unique_roles = list(speaker_mapping.values())
        if len(speaker_segments) == 2 and (unique_roles.count("agent") == 2 or unique_roles.count("customer") == 2):
            print("Conflict in gender mapping! Both speakers mapped to the same role. Falling back to duration heuristics.")
            # Assign customer to the one who spoke the most, agent to the other
            # Or just assign one to agent and one to customer arbitrarily based on order
            speakers = list(speaker_mapping.keys())
            speaker_mapping[speakers[0]] = "customer"
            speaker_mapping[speakers[1]] = "agent"
            
        # Ensure 'unknown' gets a role
        assigned_roles = set(speaker_mapping.values())
        for spk, role in speaker_mapping.items():
            if role == "unknown":
                if "customer" not in assigned_roles:
                    speaker_mapping[spk] = "customer"
                    assigned_roles.add("customer")
                else:
                    speaker_mapping[spk] = "agent"
                    assigned_roles.add("agent")
                    
        return speaker_mapping
        
    except Exception as e:
        print(f"Error in gender detection: {e}")
        return {}
