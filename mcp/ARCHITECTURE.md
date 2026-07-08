# MCP Server Architecture
## AI Trust & Safety Engine — Engineering Memory System

**Document Version:** 1.0.0
**Status:** Authoritative Design

---

## 1. Purpose

This document defines the complete architecture of the Enterprise MCP (Model Context Protocol)
Server for the AI Trust & Safety Engine. This is NOT a business-logic document.
This is a server-design document.

The MCP server is a read-oriented knowledge delivery system. It does not modify the project.
It observes, indexes, and serves structured knowledge about the project to any AI that connects.

---

## 2. Transport Layer

The server uses **stdio transport** (standard input/output), which is the standard MCP
transport for local development and IDE integrations. This requires no open ports,
no network configuration, and works out-of-the-box with Claude Desktop, Cursor,
Antigravity, and any other MCP-compatible AI client.

**Future:** HTTP/SSE transport will be added for remote MCP access (e.g., when the AI
runs in a cloud agent environment and needs to query the project memory remotely).

---

## 3. Server Identity

```
Server Name:     ai-trust-safety-engine
Server Version:  1.0.0
Protocol:        MCP 1.0 (stdio)
Language:        Python 3.11+
Framework:       mcp (official Anthropic Python SDK)
```

---

## 4. Knowledge Architecture

The MCP server does NOT compute answers. It serves pre-authored, human-verified knowledge
from a structured knowledge base. This is the correct design because:

- AI-generated summaries of code are probabilistic and can be wrong.
- Human-authored knowledge is authoritative and auditable.
- The knowledge base can be updated without touching server code.
- Every answer has a clear human author and timestamp.

### 4.1 Knowledge Base Structure

```
knowledge/
├── *.md                  (Top-level knowledge files, one per domain)
└── modules/
    └── *.md              (One file per system module, matches MODULE-XX in SES)
```

Every knowledge file follows a standard header:
```markdown
---
domain: project_overview | architecture | module | progress | ...
last_updated: YYYY-MM-DD
updated_by: <author>
status: current | outdated | draft
---
```

Any knowledge file with `status: outdated` is served with a warning flag in the tool response.

### 4.2 Knowledge Update Protocol

1. Engineer updates the relevant `.md` file in `mcp/knowledge/`.
2. Updates the `last_updated` and `status` fields in the file header.
3. Commits the change. The MCP server picks it up on next invocation (no restart needed).
4. The change is now permanent project memory visible to ALL AI assistants.

---

## 5. Tool Architecture

Each tool is an independently implemented Python module in `mcp/tools/`. A tool:

- Has a single responsibility (one domain of knowledge).
- Reads from the knowledge base (no side effects).
- Returns a structured Python dict that is serialized to JSON for the AI client.
- Includes `source_file`, `last_updated`, and `status` in every response.
- Is independently unit-testable without the MCP server running.

### 5.1 Tool Response Contract

Every tool response MUST include these top-level fields:

```json
{
  "tool": "tool_name",
  "source_file": "knowledge/filename.md",
  "last_updated": "YYYY-MM-DD",
  "status": "current | outdated | draft",
  "data": { ... }
}
```

If `status` is `"outdated"`, the AI client will see a warning:
> ⚠ This knowledge may be stale. Ask the developer to update `knowledge/filename.md`.

### 5.2 Tool Registry

| Tool | Knowledge Source | Input Params | Output Type |
|---|---|---|---|
| `get_project_overview` | `knowledge/project_overview.md` | none | `ProjectOverview` |
| `get_system_architecture` | `knowledge/architecture.md` | none | `Architecture` |
| `get_module_details` | `knowledge/modules/{name}.md` | `module_name: str` | `ModuleSpec` |
| `get_current_progress` | `knowledge/progress.md` | none | `ProgressReport` |
| `get_coding_standards` | `knowledge/coding_standards.md` | none | `CodingStandards` |
| `get_dependencies` | `knowledge/dependencies.md` | `filter: str?` | `DependencyList` |
| `get_known_issues` | `knowledge/known_issues.md` | `severity: str?` | `IssueList` |
| `get_roadmap` | `knowledge/roadmap.md` | `phase: str?` | `Roadmap` |
| `get_file_structure` | `knowledge/file_structure.md` | `path: str?` | `FileTree` |
| `search_knowledge` | ALL `knowledge/**/*.md` | `query: str` | `SearchResults` |

---

## 6. Search Architecture

`search_knowledge` is the only tool that reads from multiple files simultaneously.
It performs full-text keyword search across the entire knowledge base. It does NOT
use semantic embeddings (to avoid external dependencies). It uses token-based
TF-IDF ranking over the knowledge markdown corpus.

### Search Response Format

```json
{
  "tool": "search_knowledge",
  "query": "OTP detection",
  "results": [
    {
      "rank": 1,
      "file": "knowledge/modules/indian_number_intelligence.md",
      "excerpt": "...OTP detection requires 97% minimum recall...",
      "relevance_score": 0.94
    }
  ]
}
```

---

## 7. Server Entry Point: server.py

`server.py` is the single executable that starts the MCP server. Its responsibilities:

1. Initialize the MCP server instance with name and version.
2. Register all tools from the `tools/` package using a tool registry pattern.
3. Start the stdio transport loop (blocking, waits for AI client connections).
4. Handle graceful shutdown on SIGTERM/SIGINT.

No business logic lives in `server.py`. It is pure wiring.

---

## 8. Error Handling Contract

| Condition | Server Response |
|---|---|
| Knowledge file not found | `{"error": "KNOWLEDGE_NOT_FOUND", "message": "..."}` |
| Module name not recognized | `{"error": "UNKNOWN_MODULE", "available_modules": [...]}` |
| Knowledge file has `status: outdated` | Serve content + `"warning": "KNOWLEDGE_MAY_BE_STALE"` |
| Search returns no results | `{"results": [], "suggestion": "Try broader terms"}` |
| Any unexpected exception | `{"error": "INTERNAL_ERROR", "message": "..."}` (never crash the server) |

---

## 9. Dependencies

The MCP server has intentionally minimal dependencies, kept separate from the main project:

```
mcp>=1.0.0           # Official Anthropic MCP Python SDK
python-frontmatter   # Parse YAML front-matter from knowledge .md files
```

These are listed in `mcp/requirements.txt` and MUST NOT be added to the main project's
`backend/requirements.txt`. The MCP server is a separate process.

---

## 10. What This MCP Does NOT Do

To prevent scope creep, the following are explicitly out of scope for this MCP server:

- It does NOT execute code or call any AI APIs.
- It does NOT query the running FastAPI backend.
- It does NOT read live application logs.
- It does NOT perform file system discovery dynamically (knowledge is pre-authored).
- It does NOT write to any files.
- It does NOT have access to `.env` files or secrets.
- It does NOT expose any network port by default.
