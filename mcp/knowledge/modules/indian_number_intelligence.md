---
domain: module
module_id: MODULE-07
last_updated: 2026-07-08
updated_by: principal-architect
status: pending
---

# MODULE-07: Indian Number Intelligence

## Status
**NOT BUILT** — This is the highest-priority pending module.

## Purpose
Detect any numeric information spoken in any Indian language or format with forensic accuracy.
The primary target is OTP detection (97% minimum recall per SES acceptance criteria).

## Why This Is Hard
A 4-digit OTP can be spoken as:
- English digits: "five eight two one"
- Hindi: "paanch aath do ek"
- Mixed: "five aath do one"
- Grouped: "fifty-eight, twenty-one"
- With noise/filler: "so the OTP is... five... eight... two one"

## Inputs
- Normalized transcript from MODULE-06 (Normalization Engine)

## Outputs
A list of detected number entities, each containing:
- raw_text: The exact words spoken (as transcribed)
- parsed_value: The numeric value (e.g., 5821)
- number_type: PHONE | OTP | ACCOUNT_NUMBER | AMOUNT | AADHAAR_PATTERN | PAN_PATTERN | GENERIC
- speaker_id: SPEAKER_00 | SPEAKER_01
- start_time: float (seconds from audio start)
- end_time: float (seconds from audio start)
- confidence: float (0.0 to 1.0)

## Responsibilities
- Detect digits spoken in: English, Hindi, Urdu, Bengali, Tamil, Telugu, Punjabi
- Handle code-switching within a single number utterance
- Detect OTPs: 4-8 digit sequences spoken consecutively
- Detect phone numbers: 10-digit sequences with/without country code
- Detect monetary amounts with currency markers
- Detect Aadhaar patterns: 12-digit sequences
- Classify each detection by type

## Acceptance Criterion
OTP Detection Recall: ≥ 97%
OTP Detection Precision: ≥ 90%

## Dependencies
- MODULE-06: Normalization Engine

## Implementation Notes
- Build a digit word map for each supported language
- Use sliding window over normalized tokens to detect digit sequences
- Classify by length and context: 4-8 digits = potential OTP, 10 digits = potential phone
- No LLM involvement — fully deterministic
