---
domain: known_issues
last_updated: 2026-07-08
updated_by: principal-architect
status: current
---

# Known Issues & Workarounds

## CRITICAL 🔴

### ISSUE-001: GCP Credentials Path Mismatch
**Severity:** CRITICAL (blocks Gemini analysis)
**Status:** Partially resolved
**Description:** The `.env` file contains `GOOGLE_APPLICATION_CREDENTIALS` pointing to
`/Users/gulfamshaikh/graviiity/ml-key.json` which is a remote machine path. On the local
Windows development machine, the file is at `backend/gcp-credentials.json`.
**Symptom:** Server logs: `Gemini credentials missing. Analysis endpoints will return API errors.`
**Workaround:** Update `.env` locally to point to the absolute path of `backend/gcp-credentials.json`.
**Root Fix:** Each developer must set their own `GOOGLE_APPLICATION_CREDENTIALS` path in their
local `.env`. Do not commit this path to git.

---

## HIGH 🟠

### ISSUE-002: Diarization Disabled Without HF_TOKEN
**Severity:** HIGH (disables speaker attribution)
**Status:** By design for local dev — needs fix before production
**Description:** `HF_TOKEN` is not set in local `.env`. Pyannote diarization is disabled.
The pipeline still works — it transcribes with Whisper, but all speech is attributed to
a single speaker. The `turns` field in the response is empty or undefined.
**Symptom:** Server logs: `HF_TOKEN is missing. Diarization is disabled.`
**Workaround:** Transcription still works. For full diarization, add `HF_TOKEN` to `.env`.
**Root Fix:** Obtain HuggingFace token, accept Pyannote model terms, add to `.env`.

### ISSUE-003: Email Alerts Disabled Without SMTP Credentials
**Severity:** HIGH (silently disables alert delivery)
**Status:** By design for local dev
**Description:** `SMTP_USER` and `SMTP_PASS` not set — email alerts are skipped silently.
**Symptom:** Server logs: `SMTP credentials missing. Email alerts are disabled.`
**Workaround:** Add Gmail App Password to `.env` as SMTP credentials.

---

## MEDIUM 🟡

### ISSUE-004: torchcodec DLL Warnings on Windows
**Severity:** MEDIUM (log noise only — no functional impact)
**Status:** Will not fix (upstream issue)
**Description:** On Windows with PyTorch CPU build, `torchcodec` attempts to load
FFmpeg-specific DLLs (`libtorchcodec_core4.dll` through `libtorchcodec_core8.dll`) and
fails with `OSError`. This is a known incompatibility between PyTorch 2.12.0+cpu and
the installed `torchcodec` version. The server starts and operates correctly despite these warnings.
**Symptom:** Long block of OSError warnings in server startup logs before `Application startup complete.`
**Workaround:** Ignore. The warnings are harmless on this setup.
**Root Fix:** Align torchcodec version with installed PyTorch version, or uninstall torchcodec.

### ISSUE-005: BAD_WORDS_FILE Warning on Startup
**Severity:** MEDIUM (disables bad word detection)
**Status:** Resolved — requires correct path in `.env`
**Description:** The server warns if `BAD_WORDS_FILE` path does not exist.
**Symptom:** `Bad words file not found at <path>`
**Workaround:** Ensure `BAD_WORDS_FILE` in `.env` points to `backend/bad_words.txt` (absolute path).

### ISSUE-006: Frontend Uses localhost:8001 Hardcoded in AgentMonitor
**Severity:** MEDIUM (blocks production frontend deployment)
**Status:** Known, not yet fixed
**Description:** `frontend/src/views/AgentMonitor.tsx` line 74 has `http://localhost:8001`
hardcoded for the `/api/analyze-call` fetch call.
**Root Fix:** Extract backend URL to an environment variable or Vite config constant.

---

## LOW 🟢

### ISSUE-007: Dashboard Uses Mock Data Only
**Severity:** LOW (cosmetic — doesn't affect backend)
**Status:** By design for current phase
**Description:** The Dashboard and Insights views in the frontend use hardcoded mock data
from `frontend/src/data/mock.ts`. They do not query the live backend.
**Root Fix:** Phase 2 — wire Dashboard to Analytics Engine once it's built.

### ISSUE-008: In-Memory Job Storage is Not Persistent
**Severity:** LOW (acceptable for current scale)
**Status:** By design — temporary
**Description:** `job_service.py` stores jobs in a Python dict in memory.
Restarting the server loses all job history.
**Root Fix:** Replace with Redis or SQLite persistence before production deployment.
