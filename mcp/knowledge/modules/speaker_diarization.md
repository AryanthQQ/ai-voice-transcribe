---
domain: module
module_id: MODULE-05
last_updated: 2026-07-08
status: implemented-disabled
---
# MODULE-05: Speaker Diarization Engine
## Status
IMPLEMENTED but DISABLED locally (requires HF_TOKEN)
## Location
backend/app/services/diarize_service.py
## Purpose
Identify who spoke when. Attributes transcript segments to SPEAKER_00, SPEAKER_01, etc.
## Requirement
HF_TOKEN environment variable must be set. User must have accepted Pyannote model terms on HuggingFace.
## Inputs
- audio_file_path: str
## Outputs
- turns: List[dict] with speaker, text, start_time, end_time
- metrics: dict with agent_talk_time, customer_talk_time, silence_time, total_time
## Notes
- When disabled, pipeline still runs but returns empty turns array
- Maps SPEAKER_00 to 'agent', SPEAKER_01 to 'customer' by convention
