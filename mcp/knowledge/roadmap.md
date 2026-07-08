---
domain: roadmap
last_updated: 2026-07-08
updated_by: principal-architect
status: current
---

# Product Roadmap

## Phase 1: Enterprise Async SaaS (0-6 Months) — IN PROGRESS

Goal: Make the existing pipeline production-ready and add missing intelligence modules.

- [x] Asynchronous job processing
- [x] Job status polling endpoint
- [x] Environment-driven configuration
- [ ] Indian Number Intelligence (OTP, phone in spoken Indic)
- [ ] Normalization Engine (Hinglish, phonetic variants)
- [ ] PII Engine (email, Aadhaar, account numbers)
- [ ] Scam Engine (known script patterns, urgency language)
- [ ] Risk Engine (weighted score aggregation)
- [ ] Audit Log System (immutable, PII-masked)
- [ ] Multi-tenant client isolation
- [ ] Production CORS restriction + rate limiting
- [ ] Persistent job storage (Redis or SQLite)

## Phase 2: Predictive Acoustic Analysis (6-12 Months)

Goal: Go beyond text — analyze the voice signal itself.

- [ ] Acoustic emotion detection (pitch, volume, speaking rate)
- [ ] Interruption and talking-over pattern detection
- [ ] Silence-as-signal analysis (suspiciously long pauses)
- [ ] Speaker stress index (acoustic distress markers)
- [ ] Analytics Engine (time-series aggregation, trend detection)
- [ ] Live dashboard wired to real backend data (replacing mock data)
- [ ] Client-configurable risk weights per violation type

## Phase 3: Real-Time Streaming Moderation (12-24 Months)

Goal: From post-call to in-call intervention.

- [ ] WebSocket streaming API for live audio chunks
- [ ] Per-chunk incremental analysis with running risk accumulation
- [ ] Real-time alert trigger when CRITICAL threshold crossed mid-call
- [ ] SDK: Python, JavaScript/TypeScript, Go
- [ ] Kubernetes Helm chart for horizontal auto-scaling
- [ ] Multi-region deployment with data residency controls

## Phase 4: On-Premise and SaaS (Year 2+)

Goal: Full enterprise and regulated-industry deployment.

- [ ] Full SaaS multi-tenancy with usage metering (per audio minute)
- [ ] Self-hosted deployment package (all models downloadable)
- [ ] Kubernetes Helm chart for air-gapped deployments
- [ ] SOC 2 Type II compliance readiness
- [ ] DPDP Act (India) compliance controls
- [ ] White-label API offering for platform integrators
