"""
AI Trust & Safety Engine — Enterprise MCP Server
=================================================
Entry point. Wires all tools and starts the stdio transport loop.

Usage:
    python mcp/server.py

Compatible clients:
    Claude Desktop, Cursor, Antigravity, Aider, any MCP-compatible AI.

Architecture:
    See mcp/ARCHITECTURE.md for the full design specification.

Tool implementation status:
    [x] scan_project        — Live repository scanner (reads actual files via AST)
    [ ] get_project_overview    — Stub (reads knowledge/project_overview.md)
    [ ] get_system_architecture — Stub (reads knowledge/architecture.md)
    [ ] get_module_details      — Stub (reads knowledge/modules/{name}.md)
    [ ] get_current_progress    — Stub (reads knowledge/progress.md)
    [ ] get_coding_standards    — Stub (reads knowledge/coding_standards.md)
    [ ] get_dependencies        — Stub (reads knowledge/dependencies.md)
    [ ] get_known_issues        — Stub (reads knowledge/known_issues.md)
    [ ] get_roadmap             — Stub (reads knowledge/roadmap.md)
    [ ] get_file_structure      — Stub (reads knowledge/file_structure.md)
    [ ] search_knowledge        — Stub (TF-IDF over all knowledge/*.md)
"""

import sys
from pathlib import Path

# Ensure the mcp/ directory is on the Python path so tools/ imports work
# regardless of where the server is launched from.
_MCP_DIR = Path(__file__).resolve().parent
if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Import tool handlers
# ---------------------------------------------------------------------------
from tools.project_scanner import handle as _project_scanner_handle

# ---------------------------------------------------------------------------
# Server instantiation
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="ai-trust-safety-engine",
    version="1.0.0",
    instructions=(
        "You are connected to the Engineering Memory Server for the "
        "AI Trust & Safety Engine project. "
        "Start any session by calling scan_project() to get the ground-truth "
        "view of the repository. "
        "Then call knowledge-base tools (get_current_progress, get_system_architecture, etc.) "
        "for authoritative design context."
    ),
)

# ---------------------------------------------------------------------------
# Tool: scan_project
# ---------------------------------------------------------------------------
@mcp.tool()
def scan_project(project_root: str = "") -> dict:
    """
    Scan the entire repository and return rich project metadata from actual files on disk.

    This is a LIVE scanner — it reads the repository every time it is called.
    It does NOT use the knowledge base. It is the ground-truth about what exists.

    Reads:
    - All folders and files (depth-limited tree)
    - All Python files (AST-parsed: imports, classes, functions, FastAPI routes)
    - Config files (.env.example, pyproject.toml, tsconfig.json, package.json, etc.)
    - README files
    - requirements*.txt files (parsed to package + version_spec)
    - Dockerfile and docker-compose.yml
    - systemd .service / .socket / .timer unit files

    Returns:
    - summary: high-level metadata (file counts, frameworks detected, routes found)
    - directory_tree: annotated folder/file tree (4 levels deep)
    - api_routes: all FastAPI routes discovered via AST
    - classes: all Python classes with method lists
    - python_files: per-file analysis (imports, classes, functions, routes)
    - config_files: file path -> raw content
    - requirements: file path -> [{package, version_spec}]
    - dockerfiles: file path -> raw content
    - systemd_units: file path -> raw content
    - readme: content of the first README found

    Args:
        project_root: Optional absolute path to the repo root.
                      Leave empty to auto-detect (default: repo root).
    """
    return _project_scanner_handle(project_root or None)


# ---------------------------------------------------------------------------
# Tool: get_current_progress  (knowledge-based, stub → to be fully implemented)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_current_progress() -> dict:
    """
    Return the current engineering progress from the knowledge base.

    Shows: completed features, in-progress work, pending backlog, and blockers.
    This is the SECOND tool to call after scan_project() in any session.

    Source: mcp/knowledge/progress.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "progress.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_current_progress",
        "source_file": "mcp/knowledge/progress.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_system_architecture  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_system_architecture() -> dict:
    """
    Return the 6-layer system architecture, module implementation status map,
    current data flow, and API contracts.

    Source: mcp/knowledge/architecture.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "architecture.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_system_architecture",
        "source_file": "mcp/knowledge/architecture.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_module_details  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_module_details(module_name: str) -> dict:
    """
    Return the full specification for a specific system module.

    Available modules:
        downloader, audio_validator, vad, speech_recognition, speaker_diarization,
        normalization, indian_number_intelligence, pii_engine, abuse_engine,
        threat_engine, scam_engine, risk_engine, reasoning_engine, alert_engine,
        analytics_engine, audit_log

    Args:
        module_name: The module identifier (e.g., "indian_number_intelligence")

    Source: mcp/knowledge/modules/{module_name}.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "modules" / f"{module_name}.md"
    available = [f.stem for f in (_MCP_DIR / "knowledge" / "modules").glob("*.md")]

    if not knowledge_file.exists():
        return {
            "error": "UNKNOWN_MODULE",
            "message": f"No knowledge file for module: {module_name}",
            "available_modules": sorted(available),
        }
    return {
        "tool": "get_module_details",
        "module_name": module_name,
        "source_file": f"mcp/knowledge/modules/{module_name}.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_known_issues  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_known_issues() -> dict:
    """
    Return all known issues, active bugs, workarounds, and technical debt.
    Check this BEFORE investigating any unexpected behaviour — it may already be documented.

    Source: mcp/knowledge/known_issues.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "known_issues.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_known_issues",
        "source_file": "mcp/knowledge/known_issues.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_coding_standards  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_coding_standards() -> dict:
    """
    Return the 12 mandatory engineering principles (P-01 through P-12)
    and all project coding conventions.

    Read this before writing any code for this project.

    Source: mcp/knowledge/coding_standards.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "coding_standards.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_coding_standards",
        "source_file": "mcp/knowledge/coding_standards.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_dependencies  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_dependencies() -> dict:
    """
    Return all project dependencies with their purpose, version notes,
    and self-hosted alternatives (per the no-vendor-lock-in principle).

    Source: mcp/knowledge/dependencies.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "dependencies.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_dependencies",
        "source_file": "mcp/knowledge/dependencies.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_roadmap  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_roadmap() -> dict:
    """
    Return the 4-phase product roadmap: Phase 1 (current), Phase 2, Phase 3, Phase 4.

    Source: mcp/knowledge/roadmap.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "roadmap.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_roadmap",
        "source_file": "mcp/knowledge/roadmap.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: get_file_structure  (knowledge-based)
# ---------------------------------------------------------------------------
@mcp.tool()
def get_file_structure() -> dict:
    """
    Return the annotated project file structure — every file and folder
    with a human explanation of its purpose.

    Note: For the live disk view, use scan_project() instead.

    Source: mcp/knowledge/file_structure.md
    """
    knowledge_file = _MCP_DIR / "knowledge" / "file_structure.md"
    if not knowledge_file.exists():
        return {"error": "KNOWLEDGE_NOT_FOUND", "file": str(knowledge_file)}
    return {
        "tool": "get_file_structure",
        "source_file": "mcp/knowledge/file_structure.md",
        "content": knowledge_file.read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# Tool: search_knowledge  (searches all knowledge/*.md files)
# ---------------------------------------------------------------------------
@mcp.tool()
def search_knowledge(query: str) -> dict:
    """
    Full-text search across the entire MCP knowledge base.

    Searches all .md files in mcp/knowledge/ (including modules/).
    Returns ranked results (top 5) with file path, matched excerpt, and score.

    Use this when you don't know which specific tool to call.

    Args:
        query: Free-text search (e.g. "OTP detection", "Pyannote", "risk score")
    """
    if not query or not query.strip():
        return {
            "error": "EMPTY_QUERY",
            "message": "Please provide a non-empty search query.",
        }

    knowledge_dir = _MCP_DIR / "knowledge"
    query_tokens = set(query.lower().split())
    results = []

    for md_file in knowledge_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        content_lower = content.lower()
        # Count how many query tokens appear in this file
        score = sum(1 for token in query_tokens if token in content_lower)
        if score == 0:
            continue

        # Extract a relevant excerpt around the first matched token
        excerpt = ""
        for token in query_tokens:
            idx = content_lower.find(token)
            if idx != -1:
                start = max(0, idx - 80)
                end = min(len(content), idx + 200)
                excerpt = "..." + content[start:end].replace("\n", " ").strip() + "..."
                break

        results.append({
            "file": str(md_file.relative_to(_MCP_DIR)),
            "relevance_score": score,
            "excerpt": excerpt,
        })

    # Sort by score descending, return top 5
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_results = results[:5]

    return {
        "tool": "search_knowledge",
        "query": query,
        "total_matches": len(results),
        "results": top_results,
        "suggestion": (
            "Try broader or alternative terms."
            if not top_results else None
        ),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
