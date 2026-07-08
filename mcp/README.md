# Enterprise MCP Server — AI Trust & Safety Engine
**Model Context Protocol Server for AI Engineering Assistants**

> This server is NOT for end users.
> This server is the **permanent engineering memory** of the AI Trust & Safety Engine project.
> Any AI (Claude, ChatGPT, Gemini, Cursor, Copilot, Aider, Antigravity) can connect here
> and instantly understand this entire project without asking the developer a single question.

---

## What Is This?

This MCP Server is the single source of truth for every AI assistant working on this codebase.
Instead of an AI asking "what does this service do?" or "what is the current status?",
the AI calls a tool and receives structured, authoritative, timestamped answers.

**Eliminates:**
- Redundant onboarding questions across AI sessions
- Context loss between conversations
- Inconsistent architecture understanding
- AI hallucinating project structure

**Provides:**
- Instant, accurate project understanding for any connected AI
- A living knowledge base that grows with the project
- Structured, machine-readable answers with provenance
- Full searchability across all project domains

---

## Available Tools

| Tool | Description |
|---|---|
| `get_project_overview` | Mission, product philosophy, target users, current status |
| `get_system_architecture` | 6-layer architecture, data flow, module dependency map |
| `get_module_details` | Deep specification for any specific module (by name) |
| `get_current_progress` | What is built, in-progress, and pending |
| `get_coding_standards` | Engineering principles P-01 through P-12, conventions |
| `get_dependencies` | All libraries, their purpose, version, upgrade notes |
| `get_known_issues` | Active bugs, workarounds, technical debt |
| `get_roadmap` | Short, medium, long-term roadmap with phases |
| `get_file_structure` | Annotated project directory map with explanations |
| `search_knowledge` | Full-text search across the entire knowledge base |

---

## Connect This MCP

### Claude Desktop
```json
{
  "mcpServers": {
    "ai-trust-safety": {
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "<absolute path to ai-speech-analytics-agent>"
    }
  }
}
```

### Cursor / VS Code with MCP Extension
```json
{
  "mcp.servers": [
    {
      "name": "AI Trust & Safety Engine",
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "<absolute path to ai-speech-analytics-agent>"
    }
  ]
}
```

---

## Setup

```bash
cd mcp/
pip install -r requirements.txt
python server.py
```

---

## Directory Map

```
mcp/
├── README.md            <- You are here. Entry point for all AI engineers.
├── ARCHITECTURE.md      <- Full MCP server design specification
├── server.py            <- MCP server entry point (stdio transport)
├── requirements.txt     <- Python dependencies for the MCP server
├── tools/               <- One file per MCP tool, each independently testable
│   ├── __init__.py
│   ├── project_overview.py
│   ├── system_architecture.py
│   ├── module_details.py
│   ├── current_progress.py
│   ├── coding_standards.py
│   ├── dependencies.py
│   ├── known_issues.py
│   ├── roadmap.py
│   ├── file_structure.py
│   └── search_knowledge.py
├── knowledge/           <- Markdown knowledge base. Edit these files to update AI memory.
│   ├── project_overview.md
│   ├── architecture.md
│   ├── progress.md
│   ├── coding_standards.md
│   ├── dependencies.md
│   ├── known_issues.md
│   ├── roadmap.md
│   ├── file_structure.md
│   └── modules/         <- One file per system module
│       ├── downloader.md
│       ├── audio_validator.md
│       ├── vad.md
│       ├── speech_recognition.md
│       ├── speaker_diarization.md
│       ├── normalization.md
│       ├── indian_number_intelligence.md
│       ├── pii_engine.md
│       ├── abuse_engine.md
│       ├── threat_engine.md
│       ├── scam_engine.md
│       ├── risk_engine.md
│       ├── reasoning_engine.md
│       ├── alert_engine.md
│       ├── analytics_engine.md
│       └── audit_log.md
└── schemas/             <- JSON schemas for every tool's output
    ├── project_overview.schema.json
    ├── architecture.schema.json
    ├── module_details.schema.json
    ├── progress.schema.json
    ├── standards.schema.json
    ├── dependencies.schema.json
    ├── known_issues.schema.json
    ├── roadmap.schema.json
    ├── file_structure.schema.json
    └── search_result.schema.json
```
