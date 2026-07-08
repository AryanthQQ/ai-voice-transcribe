---
domain: dependencies
last_updated: 2026-07-08
updated_by: principal-architect
status: current
---

# Project Dependencies

## Backend (backend/requirements.txt)

| Package | Version | Purpose | Replaceable With |
|---|---|---|---|
| `fastapi` | latest | HTTP API framework | Flask, Starlette |
| `uvicorn` | latest | ASGI server for FastAPI | Hypercorn, Gunicorn+uvicorn |
| `pydantic-settings` | latest | Environment variable parsing into typed Settings | python-dotenv + dataclass |
| `python-multipart` | latest | Required by FastAPI for Form data (audio URL form fields) | N/A |
| `faster-whisper` | latest | Speech recognition — Whisper large-v3 in int8 | OpenAI Whisper, whisper.cpp |
| `pyannote.audio` | latest | Speaker diarization (who spoke when) | NVIDIA NeMo |
| `google-genai` | latest | Gemini access via Vertex AI | Vertex AI SDK, litellm |
| `librosa` | latest | Audio processing utilities | soundfile + scipy |
| `torch` (CPU) | 2.12.0+cpu | PyTorch tensor framework (required by Whisper + Pyannote) | torch CUDA build (if GPU available) |
| `psutil` | latest | CPU/memory metrics for /metrics endpoint | resource module |

## Backend — Python Standard Library (no install needed)
- `os`, `pathlib` — environment and file system
- `asyncio` — async support
- `tempfile` — secure temporary audio file handling
- `logging` — structured logging
- `smtplib`, `email` — email alert delivery
- `re` — regex patterns for violation detection
- `json` — response serialization

## Frontend (frontend/package.json — key dependencies)
| Package | Purpose |
|---|---|
| `react`, `react-dom` | UI framework |
| `typescript` | Type safety |
| `vite` | Build tool and dev server |
| `recharts` | Charts on Dashboard and Insights views |
| `lucide-react` | Icon library |
| `axios` | HTTP client (used in MCP server integration) |
| `tailwindcss` | Utility CSS (if configured) |

## MCP Server (mcp/requirements.txt)
| Package | Purpose |
|---|---|
| `mcp>=1.0.0` | Official Anthropic MCP Python SDK (stdio transport) |
| `python-frontmatter` | Parse YAML front-matter from knowledge .md files |

## Key Upgrade Notes
- `torch` must stay on the **CPU** build (`+cpu` index URL) on the local Windows machine.
  Installing the CUDA build will cause `libnvrtc.so` errors on machines without Nvidia GPU.
- `pyannote.audio` requires accepting HuggingFace model terms before `HF_TOKEN` works.
- `google-genai` SDK requires `GOOGLE_APPLICATION_CREDENTIALS` in `os.environ` to
  authenticate — set by `config.py` at startup.
