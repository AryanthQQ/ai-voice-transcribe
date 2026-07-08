---
domain: module
module_id: MODULE-12
last_updated: 2026-07-08
status: not-built
---
# MODULE-12: Risk Engine
## Status
NOT BUILT
## Purpose
Aggregate all detection outputs into a single calibrated risk score (0-100) and risk tier.
## Inputs
- Outputs of MODULE-08 (PII), MODULE-09 (Abuse), MODULE-10 (Threat), MODULE-11 (Scam)
- Call metadata (duration, speaker count, platform type)
## Outputs
- risk_score: int (0-100)
- risk_tier: LOW | MEDIUM | HIGH | CRITICAL
- contributing_factors: List[dict] with factor name and weight
- recommended_action: PASS | REVIEW | ESCALATE | AUTO_ACTION
## Design Requirements
- Fully deterministic given same inputs and weights
- Weights must be configurable per client without code changes
- Combination effects: threat + OTP request = severely elevated score
