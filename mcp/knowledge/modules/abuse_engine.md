---
domain: module
module_id: MODULE-09
last_updated: 2026-07-08
status: partial
---
# MODULE-09: Abuse Engine
## Status
PARTIAL — Basic bad-word list matching only
## Location
backend/app/services/violation_service.py
## Current Implementation
Loads bad words from BAD_WORDS_FILE (configurable env var). Case-insensitive substring matching against the full transcript.
## Inputs
- transcript: str
- bad_words: List[str] (loaded from file)
## Outputs
- bad_words_detected: List[str] (matched words)
- bad_word_count: int
## What Is Missing
- Phonetic variant matching (madarchaud != madarchod detection)
- Severity classification (MILD / MODERATE / SEVERE / EXTREME)
- Type classification (PROFANITY / PERSONAL_ATTACK / GENDER_ABUSE / CASTEIST_SLUR)
- Speaker attribution (which speaker said the bad word?)
- Timestamp of each detection
