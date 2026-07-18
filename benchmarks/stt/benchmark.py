import argparse
import json
import time
import datetime
from pathlib import Path

from models import get_stt_model
from utils import get_system_info, get_audio_info

def parse_args():
    parser = argparse.ArgumentParser(description="Standalone STT Benchmarking Framework")
    parser.add_argument("--model", type=str, required=True, help="STT Model to benchmark (e.g. large-v3, distil-large-v3, tiny)")
    parser.add_argument("--audio", type=str, required=True, help="Path to the audio file")
    return parser.parse_args()

def main():
    args = parse_args()
    
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Error: Audio file not found at {audio_path}")
        return

    print(f"Initializing STT Benchmark for model: {args.model}")
    print(f"Target Audio: {args.audio}")

    # Load Model — timed separately
    stt_engine = get_stt_model(args.model)
    load_start = time.perf_counter()
    stt_engine.load()
    load_end = time.perf_counter()
    model_load_time = load_end - load_start

    print(f"Model loaded in {model_load_time:.2f}s")

    # Collect Audio Metadata
    audio_info = get_audio_info(str(audio_path))
    audio_duration = audio_info["duration"]

    print("Starting transcription benchmark...")
    
    # Benchmarking — transcription only
    transcribe_start = time.perf_counter()
    full_transcript, segments, detected_language, language_confidence = stt_engine.transcribe(str(audio_path))
    transcribe_end = time.perf_counter()
    
    transcription_time = transcribe_end - transcribe_start
    processing_time = model_load_time + transcription_time
    rtf = transcription_time / audio_duration if audio_duration > 0 else 0

    print(f"Transcription Complete. Transcription Time: {transcription_time:.2f}s | Model Load Time: {model_load_time:.2f}s | Total Processing Time: {processing_time:.2f}s | RTF: {rtf:.2f}")

    # Collect System Metadata
    system_info = get_system_info()

    # Determine framework versions
    import faster_whisper
    import ctranslate2

    # Prepare JSON Payload
    results = {
        "model": args.model,
        "framework": "faster_whisper",
        "framework_version": faster_whisper.__version__,
        "ctranslate2_version": ctranslate2.__version__,
        
        "model_load_time": model_load_time,
        "transcription_time": transcription_time,
        "processing_time": processing_time,
        "audio_duration": audio_duration,
        "rtf": rtf,
        
        "language": detected_language,
        "language_confidence": language_confidence,
        
        "system": system_info,
        
        "audio": {
            "sample_rate": audio_info["sample_rate"],
            "channels": audio_info["channels"],
            "file_size_mb": audio_info["file_size_mb"]
        },
        
        "segments": [
            {
                "start": s.start,
                "end": s.end,
                "text": s.text
            } for s in segments
        ],
        
        "transcript": full_transcript
    }

    # Save outputs
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(__file__).resolve().parent
    
    results_dir = base_dir / "results"
    transcripts_dir = base_dir / "transcripts"
    
    results_dir.mkdir(exist_ok=True)
    transcripts_dir.mkdir(exist_ok=True)

    json_path = results_dir / f"{timestamp}.json"
    txt_path = transcripts_dir / f"{timestamp}.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(full_transcript)

    print(f"Saved JSON result: {json_path}")
    print(f"Saved transcript: {txt_path}")

if __name__ == "__main__":
    main()
