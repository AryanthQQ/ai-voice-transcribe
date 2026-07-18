import sys
import os
from pathlib import Path
import time
import json
import logging
from faster_whisper import WhisperModel

# Use local utils
sys.path.insert(0, r'c:\Users\hp\Desktop\ai voice transcribe\ai-speech-analytics-agent\benchmarks\stt')
from utils import get_audio_info

def run_experiment():
    dataset_path = Path(r"C:\Users\hp\Desktop\benchmark")
    
    print("Loading distil-large-v3...")
    model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8", cpu_threads=8)
    
    files = list(dataset_path.rglob("*.mp3"))
    results = []
    
    for audio_path in files:
        file_path_str = str(audio_path)
        folder = audio_path.parent.name
        
        # Determine forced language based on folder
        forced_lang = None
        if folder.lower() == "hindi":
            forced_lang = "hi"
        elif folder.lower() == "marathi":
            forced_lang = "mr"
        elif folder.lower() == "bengal":
            forced_lang = "bn"
        else:
            forced_lang = "hi" # fallback
            
        print(f"\nEvaluating: {audio_path.name} (Folder: {folder})")
        audio_info = get_audio_info(file_path_str)
        duration = audio_info["duration"]
        
        file_res = {
            "file": audio_path.name,
            "folder": folder,
            "duration": duration,
            "experiments": {}
        }
        
        # Experiment A: Automatic
        print("  Running Experiment A (language=None)...")
        start_a = time.time()
        segments_gen, info_a = model.transcribe(
            file_path_str, 
            language=None, 
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            no_speech_threshold=0.6,
            beam_size=5
        )
        text_a = " ".join([s.text.strip() for s in segments_gen])
        time_a = time.time() - start_a
        rtf_a = time_a / duration if duration > 0 else 0
        
        file_res["experiments"]["A"] = {
            "mode": "automatic",
            "detected_language": info_a.language,
            "language_probability": info_a.language_probability,
            "transcription_time": time_a,
            "rtf": rtf_a,
            "transcript": text_a
        }
        
        # Experiment B/C: Forced Language
        print(f"  Running Experiment B/C (language='{forced_lang}')...")
        start_b = time.time()
        segments_gen, info_b = model.transcribe(
            file_path_str, 
            language=forced_lang, 
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            no_speech_threshold=0.6,
            beam_size=5
        )
        text_b = " ".join([s.text.strip() for s in segments_gen])
        time_b = time.time() - start_b
        rtf_b = time_b / duration if duration > 0 else 0
        
        file_res["experiments"]["forced"] = {
            "mode": f"forced_{forced_lang}",
            "forced_language": forced_lang,
            "transcription_time": time_b,
            "rtf": rtf_b,
            "transcript": text_b
        }
        
        results.append(file_res)
        
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print("\nExperiment complete. Results saved to eval_results.json")

if __name__ == "__main__":
    run_experiment()
