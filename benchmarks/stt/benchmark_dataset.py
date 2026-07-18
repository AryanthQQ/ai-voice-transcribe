"""
benchmark_dataset.py
--------------------
Dataset-level STT benchmarking script.

Reuses the same models.py / utils.py internals as benchmark.py.
Loads the model ONCE, then runs transcription across every audio file
in the specified dataset folder.

Generates:
  - Individual JSON report per file  (results/<timestamp>_<filename>.json)
  - Individual TXT transcript per file (transcripts/<timestamp>_<filename>.txt)
  - Consolidated JSON summary report   (results/<timestamp>_SUMMARY.json)

Usage:
    python benchmark_dataset.py --model distil-large-v3 --dataset <folder_path>
"""

import argparse
import json
import time
import datetime
from pathlib import Path

from models import get_stt_model
from utils import get_system_info, get_audio_info

# Supported audio extensions
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".mp4"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dataset-level STT Benchmarking -- Distil-Whisper / Faster-Whisper"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="STT model to benchmark (e.g. distil-large-v3, large-v3)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to folder containing audio files (searched recursively)",
    )
    return parser.parse_args()


def collect_audio_files(dataset_path: Path) -> list:
    """Recursively collect all supported audio files from the dataset folder."""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(dataset_path.rglob(f"*{ext}"))
    return sorted(files)


def main():
    args = parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists() or not dataset_path.is_dir():
        print(f"Error: Dataset folder not found: {dataset_path}")
        return

    # Collect audio files
    audio_files = collect_audio_files(dataset_path)
    if not audio_files:
        print(f"Error: No supported audio files found in {dataset_path}")
        return

    print(f"\n{'='*65}")
    print(f"  Dataset Benchmark -- {args.model}")
    print(f"{'='*65}")
    print(f"  Dataset  : {dataset_path}")
    print(f"  Files    : {len(audio_files)} audio file(s) found")
    print(f"{'='*65}\n")
    for af in audio_files:
        try:
            rel = af.relative_to(dataset_path)
        except ValueError:
            rel = af.name
        print(f"   * {rel}")
    print()

    # Output directories
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    transcripts_dir = base_dir / "transcripts"
    results_dir.mkdir(exist_ok=True)
    transcripts_dir.mkdir(exist_ok=True)

    # Load model ONCE
    print(f"Loading model: {args.model} ...")
    stt_engine = get_stt_model(args.model)
    load_start = time.perf_counter()
    stt_engine.load()
    load_end = time.perf_counter()
    model_load_time = load_end - load_start
    print(f"Model loaded in {model_load_time:.2f}s\n")

    # System metadata (collected once)
    system_info = get_system_info()

    # Framework versions
    import faster_whisper
    import ctranslate2
    fw_version = faster_whisper.__version__
    ct2_version = ctranslate2.__version__

    # Benchmark timestamp prefix
    run_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Per-file benchmark loop
    benchmark_start = time.perf_counter()

    per_file_results = []
    failed_files = []

    for idx, audio_path in enumerate(audio_files, start=1):
        print(f"[{idx}/{len(audio_files)}] {audio_path.name}")
        print(f"         Path : {audio_path}")

        try:
            # Audio metadata
            audio_info = get_audio_info(str(audio_path))
            audio_duration = audio_info["duration"]

            # Transcription -- timed
            t_start = time.perf_counter()
            full_transcript, segments, detected_language, lang_confidence = \
                stt_engine.transcribe(str(audio_path))
            t_end = time.perf_counter()

            transcription_time = t_end - t_start
            processing_time = model_load_time + transcription_time
            rtf = transcription_time / audio_duration if audio_duration > 0 else 0.0

            print(f"         Duration     : {audio_duration:.2f}s")
            print(f"         Language     : {detected_language} ({lang_confidence*100:.1f}%)")
            print(f"         Transcription: {transcription_time:.2f}s")
            print(f"         RTF          : {rtf:.4f}")
            preview = full_transcript[:120] + ("..." if len(full_transcript) > 120 else "")
            print(f"         Transcript   : {preview}")
            print()

            # Build individual result payload
            file_result = {
                "file": str(audio_path),
                "filename": audio_path.name,
                "model": args.model,
                "framework": "faster_whisper",
                "framework_version": fw_version,
                "ctranslate2_version": ct2_version,

                "model_load_time": model_load_time,
                "transcription_time": transcription_time,
                "processing_time": processing_time,
                "audio_duration": audio_duration,
                "rtf": rtf,

                "language": detected_language,
                "language_confidence": lang_confidence,

                "system": system_info,

                "audio": {
                    "sample_rate": audio_info["sample_rate"],
                    "channels": audio_info["channels"],
                    "file_size_mb": audio_info["file_size_mb"],
                },

                "segments": [
                    {"start": s.start, "end": s.end, "text": s.text}
                    for s in segments
                ],

                "transcript": full_transcript,
                "status": "success",
            }

            # Save individual outputs
            safe_name = "".join(
                c if c.isalnum() or c in "-_." else "_"
                for c in audio_path.stem
            )
            json_path = results_dir / f"{run_timestamp}_{safe_name}.json"
            txt_path = transcripts_dir / f"{run_timestamp}_{safe_name}.txt"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(file_result, f, indent=4, ensure_ascii=False)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_transcript)

            print(f"         JSON : {json_path.name}")
            print(f"         TXT  : {txt_path.name}")
            print()

            per_file_results.append(file_result)

        except Exception as e:
            print(f"         ERROR: {e}\n")
            failed_files.append({"file": str(audio_path), "error": str(e)})

    # Consolidated summary
    benchmark_end = time.perf_counter()
    total_benchmark_time = benchmark_end - benchmark_start

    successful = [r for r in per_file_results if r.get("status") == "success"]

    avg_transcription_time = (
        sum(r["transcription_time"] for r in successful) / len(successful)
        if successful else 0.0
    )
    avg_rtf = (
        sum(r["rtf"] for r in successful) / len(successful)
        if successful else 0.0
    )
    avg_audio_duration = (
        sum(r["audio_duration"] for r in successful) / len(successful)
        if successful else 0.0
    )
    languages_detected = list({r["language"] for r in successful})

    summary = {
        "benchmark_run": run_timestamp,
        "model": args.model,
        "framework": "faster_whisper",
        "framework_version": fw_version,
        "ctranslate2_version": ct2_version,
        "dataset": str(dataset_path),

        "total_files": len(audio_files),
        "successful_files": len(successful),
        "failed_files_count": len(failed_files),
        "failed_files": failed_files,

        "model_load_time": model_load_time,
        "total_benchmark_time": total_benchmark_time,

        "avg_transcription_time": avg_transcription_time,
        "avg_rtf": avg_rtf,
        "avg_audio_duration": avg_audio_duration,

        "languages_detected": languages_detected,

        "system": system_info,

        "per_file_summary": [
            {
                "filename": r["filename"],
                "audio_duration": r["audio_duration"],
                "transcription_time": r["transcription_time"],
                "rtf": r["rtf"],
                "language": r["language"],
                "language_confidence": r["language_confidence"],
                "status": r["status"],
            }
            for r in per_file_results
        ] + [
            {
                "filename": Path(f["file"]).name,
                "status": "failed",
                "error": f["error"],
            }
            for f in failed_files
        ],
    }

    # Save consolidated summary
    summary_path = results_dir / f"{run_timestamp}_SUMMARY.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    # Print final report
    print(f"\n{'='*65}")
    print(f"  BENCHMARK COMPLETE -- {args.model}")
    print(f"{'='*65}")
    print(f"  Total Files         : {len(audio_files)}")
    print(f"  Successful          : {len(successful)}")
    print(f"  Failed              : {len(failed_files)}")
    print(f"  Model Load Time     : {model_load_time:.2f}s")
    print(f"  Total Bench Time    : {total_benchmark_time:.2f}s")
    print(f"  Avg Transcription   : {avg_transcription_time:.2f}s")
    print(f"  Avg RTF             : {avg_rtf:.4f}")
    print(f"  Avg Audio Duration  : {avg_audio_duration:.2f}s")
    langs = ", ".join(languages_detected) if languages_detected else "N/A"
    print(f"  Languages Detected  : {langs}")
    print(f"  Summary Report      : {summary_path}")
    print(f"{'='*65}\n")

    if failed_files:
        print("Failed files:")
        for ff in failed_files:
            print(f"  x {Path(ff['file']).name} -- {ff['error']}")
        print()


if __name__ == "__main__":
    main()
