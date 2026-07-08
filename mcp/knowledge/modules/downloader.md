---
domain: module
module_id: MODULE-01
last_updated: 2026-07-08
status: implemented
---
# MODULE-01: Downloader
## Status
IMPLEMENTED — Inside worker_service.py
## Location
backend/app/services/worker_service.py (first section of process_call_audio_async)
## Purpose
Download raw audio from a remote URL to a local temp file.
## Inputs
- voice_url: str (HTTP/HTTPS URL to audio file)
## Outputs
- tmp_path: str (absolute path to downloaded temp file)
- file_size_mb: float
## Key Behavior
- Uses httpx async client
- Always deletes temp file in finally block regardless of success/failure
- Logs file size after download
## NOT YET Implemented
- SHA-256 hash for audit integrity
- Configurable max file size limit
- Retry with exponential backoff
