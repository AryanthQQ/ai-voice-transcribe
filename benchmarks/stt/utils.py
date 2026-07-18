import os
import platform
import psutil
import torchaudio

def get_system_info() -> dict:
    """Collects hardware and OS information."""
    
    # Import settings to get configured device and compute type
    import sys
    from pathlib import Path
    backend_path = str(Path(__file__).resolve().parents[2] / "backend")
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    from app.core.config import settings

    cpu_info = platform.processor() or platform.machine()
    cores = psutil.cpu_count(logical=True)
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    
    return {
        "cpu": cpu_info,
        "cores": cores,
        "ram_gb": ram_gb,
        "device": settings.WHISPER_DEVICE,
        "compute_type": settings.WHISPER_COMPUTE_TYPE,
        "os": os_info
    }

import wave

def get_audio_info(audio_path: str) -> dict:
    """Collects metadata about the audio file.

    Supports WAV (via stdlib wave) and MP3 / M4A / FLAC / OGG / MP4
    (via torchaudio.info, which is a declared project dependency).
    Both paths return an identical dict schema.
    """

    # File size
    file_size_bytes = os.path.getsize(audio_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    sample_rate = 0
    channels = 0
    duration = 0.0

    try:
        if audio_path.lower().endswith(".wav"):
            with wave.open(audio_path, "rb") as wav_file:
                channels = wav_file.getnchannels()
                sample_rate = wav_file.getframerate()
                frames = wav_file.getnframes()
                duration = frames / float(sample_rate)
        else:
            # Use PyAV for all other formats (MP3, M4A, FLAC, OGG, MP4, etc.)
            # av is a hard dependency of faster-whisper — always available.
            import av
            with av.open(audio_path) as container:
                stream = container.streams.audio[0]
                duration = float(stream.duration * stream.time_base)
                sample_rate = stream.sample_rate
                channels = stream.channels
    except Exception as e:
        print(f"Warning: Failed to extract audio metadata: {e}")

    return {
        "duration": duration,
        "sample_rate": sample_rate,
        "channels": channels,
        "file_size_mb": file_size_mb,
    }
