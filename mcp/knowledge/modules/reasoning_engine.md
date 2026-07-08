---
domain: module
module_id: MODULE-13
last_updated: 2026-07-08
status: implemented
---
# MODULE-13: Reasoning Engine (LLM Layer)
## Status
IMPLEMENTED
## Location
backend/app/services/gemini_service.py
## Purpose
Produce human-readable explanations and structured JSON verdict using Gemini.
## Model
gemini-2.5-flash-lite (configurable via GEMINI_MODEL env var)
## Authentication
Vertex AI via GOOGLE_APPLICATION_CREDENTIALS (ADC). Config.py injects this into os.environ at startup.
## Inputs
- transcript: str
- diarized_turns: List[dict]
- violations detected by violation_service (passed as context)
## Outputs
- gemini_analysis: dict (structured JSON from Gemini response)
## Critical Constraint
Gemini MUST NOT be used to detect violations. It receives pre-detected violations and explains/contextualizes them. See P-07 and P-08 in coding_standards.md.
## Known Issue
Disabled locally — GOOGLE_APPLICATION_CREDENTIALS path mismatch. See known_issues.md ISSUE-001.
