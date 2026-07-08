---
domain: module
module_id: MODULE-04
last_updated: 2026-07-08
status: implemented
---
# MODULE-04: Speech Recognition Engine
## Status
IMPLEMENTED
## Location
backend/app/services/speech_service.py
## Purpose
Convert audio to timestamped transcript using Whisper large-v3.
## Model
Whisper large-v3, int8 quantization, CPU device (configurable via WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE)
## Singleton Pattern
Whisper model is loaded once at first use and cached. Subsequent calls reuse the loaded model.
## Inputs
- audio_file_path: str
## Outputs
- transcript: str (full text)
- language: str (detected ISO language code)
- segments: List[dict] with text, start, end, words
## Notes
- translate=True mode translates any language to English (currently used in agent monitor)
- VAD filter enabled by default to reduce hallucination
