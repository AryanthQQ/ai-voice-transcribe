# ADR 001: STT Model Selection

## Status
Accepted

## Context
Our platform handles heavily code-switched audio (Hindi/Hinglish/English) from Friendship Hub interactions. The accuracy of downstream modules (like Contact Detection and NLP Analysis) heavily depends on the transcription accuracy of the Speech-to-Text (STT) layer.

We evaluated several open-source, commercial-friendly STT models running locally on CPU. The primary candidates were models from the Whisper ecosystem.

## Decision

### Official Configuration

- **Framework:** `faster-whisper`
- **Primary Model:** `large-v3-turbo`
- **Device:** `cpu`
- **Compute Type:** `int8`

### Rationale

`large-v3-turbo` provides the best balance between speed and transcription quality. Our benchmark testing on real Friendship Hub datasets confirmed that it operates at roughly 1.0 RTF (Real-Time Factor) on standard CPUs using `int8` quantization while successfully recognizing native scripts (Devanagari, Bengali) and English loan words.

### Rejected Models

**distil-large-v3** is officially REJECTED for this project and must not be used outside of isolated research.

*Reasons for Rejection:*
1. **English Bias:** Distil-Whisper applies strong English linguistic priors, meaning it forcibly translates Hinglish or Hindi speech into English rather than transcribing the phonetic equivalent.
2. **Hallucinations:** The model was prone to injecting repetitive phrases or entirely hallucinated text during periods of silence.
3. **Failed Benchmarks:** It completely failed the 16-call Friendship Hub benchmark dataset when evaluated against native Indian speakers.

### Fallback Model

- **Fallback Model:** `large-v3`

The standard `large-v3` is identical in architecture but is un-distilled and un-pruned (compared to turbo). It is retained as a strictly documented fallback option if `large-v3-turbo` experiences edge-case regressions in production. It is not loaded automatically; a developer or dev-ops engineer must manually update the configuration `STT_PRIMARY_MODEL` to fallback.

## Model Decision History

1. **Initial Exploration:** `distil-large-v3` was tested for its speed advantages.
2. **Benchmark Sprint:** 16-call dataset testing revealed catastrophic failure on code-switched Hinglish.
3. **Evaluation:** `large-v3-turbo` was benchmarked as an alternative.
4. **Final Decision:** `large-v3-turbo` chosen as official primary model; configuration standardized under `STT_*` environment variables in Pydantic.
