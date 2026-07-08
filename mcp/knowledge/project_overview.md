---
domain: project_overview
last_updated: 2026-07-08
updated_by: principal-architect
status: current
---

# Project Overview: AI Trust & Safety Engine

## Mission
Build India's most accurate multilingual AI Voice Moderation Platform.
Analyze recorded call audio and detect policy violations with enterprise-level accuracy,
with a primary focus on Indian languages.

## What We Are NOT
This is NOT a Speech-to-Text application.
This is NOT a transcription tool.
Converting audio to words is infrastructure, not product.

## What We ARE
We are an enterprise Trust & Safety Intelligence Engine.
We produce structured, explainable, timestamped, confidence-scored risk intelligence
derived from voice conversations.

## Target Users
- Dating apps and matrimony platforms (verbal abuse, harassment, grooming)
- Voice chat and gaming platforms (toxicity, bullying)
- Customer support and call centers (QA automation, compliance, PII leaks)
- Social audio communities (hate speech, radicalization)

## Why This Matters for India
India speaks 22+ scheduled languages with 780+ dialects.
Urban population communicates in code-switched blends (Hinglish, Tanglish).
No global vendor prioritizes Indic language moderation at this depth.
This is our market and our moat.

## Current Backend Status (as of 2026-07-08)
### Implemented and Running
- FastAPI backend on port 8001
- Asynchronous job processing (BackgroundTasks)
- Job status polling endpoint (GET /api/analyze-status/{job_id})
- Whisper large-v3 speech recognition (CPU, int8)
- Pyannote speaker diarization (disabled locally — requires HF_TOKEN)
- Gemini analysis via Vertex AI (GCP ADC authentication)
- Violation detection service (bad words, phone numbers, threats)
- Email alert service (SMTP)
- Health endpoint (GET /health)
- Metrics endpoint (GET /metrics)
- CORS middleware (allow all origins — restrict before production)
- Environment-driven configuration (config.py + .env)
- BAD_WORDS_FILE configurable via environment variable

### NOT Yet Implemented
- Indian Number Intelligence module (OTP/phone spoken-word parsing)
- PII Engine (email addresses, Aadhaar patterns)
- Scam Engine (script pattern detection)
- Risk Engine (weighted score aggregation)
- Normalization Engine (Hinglish/transliteration)
- Analytics Engine (time-series aggregation)
- Audit Log System
- Multi-tenant configuration
- Real-time streaming

## Repository Location
`c:\Users\hp\Desktop\ai voice transcribe\ai-speech-analytics-agent\`
