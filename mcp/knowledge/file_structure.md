---
domain: file_structure
last_updated: 2026-07-08
updated_by: principal-architect
status: current
---

# Annotated Project File Structure

```
ai-speech-analytics-agent/
│
├── .env                          # Active secrets — NEVER commit to git
├── .env.example                  # Template with all required variables and comments
├── .gitignore
│
├── backend/                      # Python FastAPI backend
│   ├── run.py                    # Uvicorn launcher — entry point to start the server
│   ├── requirements.txt          # Python dependencies for the backend
│   ├── bad_words.txt             # Configurable bad-words list (set BAD_WORDS_FILE env var)
│   ├── gcp-credentials.json      # GCP service account key — NEVER commit to git
│   │
│   └── app/
│       ├── main.py               # FastAPI app: CORS, exception handlers, routers, startup
│       │
│       ├── core/
│       │   ├── config.py         # All settings via pydantic-settings (reads from .env)
│       │   └── logger.py         # Structured logger: "ai-speech-analytics"
│       │
│       ├── api/
│       │   └── routes/
│       │       ├── analyze.py    # POST /api/analyze-call + GET /api/analyze-status/{job_id}
│       │       └── transcribe.py # POST /api/transcribe (direct transcription)
│       │
│       ├── schemas/
│       │   ├── requests.py       # Pydantic request models
│       │   └── responses.py      # Pydantic response models (AnalyzeCallResponse, etc.)
│       │
│       ├── services/
│       │   ├── worker_service.py     # ORCHESTRATOR: runs full pipeline, called by BackgroundTasks
│       │   ├── job_service.py        # In-memory job state: create, update, get (singleton)
│       │   ├── speech_service.py     # Whisper large-v3 transcription (singleton model)
│       │   ├── diarize_service.py    # Pyannote speaker diarization (requires HF_TOKEN)
│       │   ├── gemini_service.py     # Vertex AI Gemini analysis via GCP ADC
│       │   ├── violation_service.py  # Deterministic detection: bad words, phones, threats
│       │   ├── email_service.py      # SMTP email alerts (requires SMTP_* env vars)
│       │   ├── transliterate_service.py  # Romanized Indic text processing utilities
│       │   └── metrics_service.py    # CPU/memory metrics via psutil (GET /metrics)
│       │
│       └── utils/
│           └── (utility helpers)
│
├── frontend/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx               # Root: nav, routing between views
│   │   ├── views/
│   │   │   ├── Dashboard.tsx     # Charts and KPIs (mock data only)
│   │   │   ├── AgentMonitor.tsx  # n8n webhook trigger + async polling UI (MAIN INTEGRATION)
│   │   │   ├── Analyze.tsx       # Direct Whisper transcription (uses client-side provider)
│   │   │   ├── Insights.tsx      # Analytics insights view
│   │   │   └── Roadmap.tsx       # Project roadmap display
│   │   ├── lib/
│   │   │   ├── transcribe.ts     # Whisper provider abstraction (local/groq/openai/custom)
│   │   │   ├── analyzer.ts       # Client-side violation analysis engine (JS)
│   │   │   └── useTranscribeSettings.ts  # LocalStorage config hook (key: v3)
│   │   └── components/           # Reusable UI components
│
└── mcp/                          # MCP Server (THIS SERVER — project engineering memory)
    ├── README.md
    ├── ARCHITECTURE.md
    ├── server.py
    ├── requirements.txt
    ├── tools/                    # One file per MCP tool
    └── knowledge/                # Human-authored knowledge base (update these as project evolves)
        ├── modules/              # One .md file per system module
        └── *.md                  # Domain knowledge files
```

## Critical Files for Any New AI Engineer

| File | Why It Matters |
|---|---|
| `backend/app/core/config.py` | Every configurable setting lives here — check this first |
| `backend/app/services/worker_service.py` | The full pipeline orchestration — understand this to understand everything |
| `backend/app/services/violation_service.py` | Current detection logic — where all new detectors get added |
| `backend/app/api/routes/analyze.py` | The public API contract — do not change without updating frontend |
| `frontend/src/views/AgentMonitor.tsx` | The main integration UI used by real clients via n8n |
| `.env.example` | Required environment variables — copy to `.env` to run locally |
| `mcp/knowledge/progress.md` | What is built vs. what is not — read this before writing any code |
