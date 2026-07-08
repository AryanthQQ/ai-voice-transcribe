"""
Tool: build_context
MCP Tool Name: build_context

Purpose:
    Synthesize a complete, AI-ready context document by combining:
      1. Live project scan  (calls project_scanner internally — ground truth)
      2. Knowledge base     (architecture, progress, issues, dependencies, roadmap)

    The output is structured into 7 sections that match every dimension an AI
    engineer needs when joining a session:
      - project_summary
      - current_architecture
      - features (implemented / in_progress / pending)
      - dependencies
      - current_sprint
      - known_issues
      - current_todo

    Additionally, the `ai_ready_summary` field contains a single formatted
    markdown string that can be injected verbatim as a system prompt into
    ANY AI assistant (Claude, ChatGPT, Gemini, Cursor, etc.).

    This is the MASTER onboarding tool. One call gives you everything.

Inputs:
    include_file_tree (bool): Include the full directory tree in output.
                              Default True. Set False for lighter context.
    include_python_details (bool): Include per-file Python analysis from scanner.
                                   Default False. Set True when debugging structure.

Outputs:
    {
      "tool": "build_context",
      "generated_at": ISO8601,
      "build_duration_ms": int,
      "context": {
        "project_summary":       {...},
        "current_architecture":  {...},
        "features":              {implemented, in_progress, pending},
        "dependencies":          [{package, version_spec, purpose}],
        "current_sprint":        {goal, in_progress, blockers},
        "known_issues":          [{id, severity, title, description, workaround}],
        "current_todo":          [{priority, item, category}],
      },
      "ai_ready_summary": str,   <- Inject this into any AI as a system prompt
      "directory_tree": dict,    <- Present if include_file_tree=True
      "api_surface": [...],      <- All discovered FastAPI routes
    }

Design:
    - Calls project_scanner.handle() for live disk data (no cache)
    - Reads knowledge/*.md files for human-authored context
    - All parsing is stdlib-only (no external deps)
    - Faults in any individual section are isolated — one broken file
      does not prevent the rest of the context from being built
    - Build time target: < 5 seconds
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path bootstrap — ensure the mcp/ directory is on sys.path so that
# `from tools.project_scanner import ...` works whether this file is:
#   a) run standalone: python mcp/tools/context_builder.py
#   b) imported by server.py (which already bootstraps its own sys.path)
# ---------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parent
_MCP_DIR = _TOOLS_DIR.parent
_KNOWLEDGE_DIR = _MCP_DIR / "knowledge"

if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))

# Import the scanner (same package, no circular dependency)
from tools.project_scanner import handle as _run_scanner


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# (All stdlib — no markdown library needed for our structured .md files)
# ---------------------------------------------------------------------------

def _read_knowledge(filename: str) -> Optional[str]:
    """Read a knowledge file. Returns None if not found."""
    path = _KNOWLEDGE_DIR / filename
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _strip_frontmatter(content: str) -> str:
    """Remove YAML front-matter (--- ... ---) from markdown content."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip("\n")
    return content


def _parse_frontmatter(content: str) -> dict:
    """Extract key: value pairs from YAML front-matter block."""
    meta = {}
    if not content.startswith("---"):
        return meta
    end = content.find("---", 3)
    if end == -1:
        return meta
    block = content[3:end].strip()
    for line in block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta


def _parse_checklist(content: str) -> dict[str, list[str]]:
    """
    Parse markdown checklist items into three buckets:
        done      : - [x] item
        in_progress: - [/] item  (custom notation)
        pending   : - [ ] item

    Ignores numbered list items (1. 2. etc.) which are parsed separately.
    Returns items as plain text (stripped of backticks and markdown).
    """
    done = []
    in_progress = []
    pending = []

    for line in content.splitlines():
        stripped = line.strip()
        # Normalize: remove bold (**), backticks, inline code
        clean = re.sub(r"`[^`]+`", lambda m: m.group(0).strip("`"), stripped)
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean)
        clean = clean.strip()

        if re.match(r"^-\s*\[x\]\s*", clean, re.IGNORECASE):
            text = re.sub(r"^-\s*\[x\]\s*", "", clean, flags=re.IGNORECASE).strip()
            if text:
                done.append(text)
        elif re.match(r"^-\s*\[/\]\s*", clean, re.IGNORECASE):
            text = re.sub(r"^-\s*\[/\]\s*", "", clean, flags=re.IGNORECASE).strip()
            if text:
                in_progress.append(text)
        elif re.match(r"^-\s*\[\s\]\s*", clean):
            text = re.sub(r"^-\s*\[\s\]\s*", "", clean).strip()
            if text:
                pending.append(text)

    return {"done": done, "in_progress": in_progress, "pending": pending}


def _parse_numbered_list(content: str) -> list[str]:
    """
    Extract items from markdown numbered lists (1. 2. 3. format).
    Used for extracting prioritized backlog items.
    """
    items = []
    for line in content.splitlines():
        m = re.match(r"^\s*\d+\.\s+(.+)$", line.strip())
        if m:
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", m.group(1)).strip()
            items.append(text)
    return items


def _parse_markdown_table(content: str) -> list[dict]:
    """
    Parse the first markdown table found in content.
    Returns list of row dicts keyed by lowercased header names.
    """
    lines = content.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r"^\|[\s\-:|]+\|", next_line):
                header_idx = i
                break

    if header_idx is None:
        return []

    headers = [h.strip().lower() for h in lines[header_idx].split("|") if h.strip()]
    rows = []
    for line in lines[header_idx + 2:]:
        if not line.strip().startswith("|"):
            break
        cells = [c.strip() for c in line.split("|") if c.strip() != ""]
        if len(cells) >= len(headers):
            rows.append(dict(zip(headers, cells)))

    return rows


def _extract_section(content: str, heading: str) -> str:
    """
    Extract the content of a markdown section identified by its heading.
    Returns everything from the heading line until the next same-level heading.
    """
    lines = content.splitlines()
    # Detect heading level
    level = 0
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("#") and heading.lower() in line.lower():
            level = len(re.match(r"^(#+)", line.strip()).group(1))
            start_idx = i + 1
            break

    if start_idx is None:
        return ""

    section_lines = []
    for line in lines[start_idx:]:
        # Stop at the next heading of same or higher level
        m = re.match(r"^(#+)\s", line.strip())
        if m and len(m.group(1)) <= level:
            break
        section_lines.append(line)

    return "\n".join(section_lines).strip()


def _parse_issues(content: str) -> list[dict]:
    """
    Parse the known_issues.md file into structured issue objects.
    Detects ### ISSUE-XXX: Title blocks and extracts severity, description, workaround.
    """
    issues = []
    current = {}
    current_field = None

    for line in content.splitlines():
        # New issue block: ### ISSUE-001: Title
        m = re.match(r"^###\s+(ISSUE-\d+):\s+(.+)$", line.strip())
        if m:
            if current.get("id"):
                issues.append(current)
            current = {
                "id": m.group(1),
                "title": m.group(2).strip(),
                "severity": "",
                "status": "",
                "description": "",
                "workaround": "",
            }
            current_field = None
            continue

        if not current.get("id"):
            continue

        # Field extraction
        if line.strip().startswith("**Severity:**"):
            current["severity"] = line.split("**Severity:**", 1)[1].strip()
        elif line.strip().startswith("**Status:**"):
            current["status"] = line.split("**Status:**", 1)[1].strip()
        elif line.strip().startswith("**Description:**"):
            current["description"] = line.split("**Description:**", 1)[1].strip()
            current_field = "description"
        elif line.strip().startswith("**Workaround:**"):
            current["workaround"] = line.split("**Workaround:**", 1)[1].strip()
            current_field = "workaround"
        elif line.strip().startswith("**Root Fix:**"):
            current["root_fix"] = line.split("**Root Fix:**", 1)[1].strip()
            current_field = None
        elif line.strip() and current_field and not line.strip().startswith("**"):
            current[current_field] = (current[current_field] + " " + line.strip()).strip()

    if current.get("id"):
        issues.append(current)

    return issues


# ---------------------------------------------------------------------------
# Context assembly helpers
# ---------------------------------------------------------------------------

def _build_project_summary(scanner_result: dict) -> dict:
    """Build project summary from scanner output + project_overview knowledge."""
    overview = _read_knowledge("project_overview.md") or ""
    meta = _parse_frontmatter(overview)
    body = _strip_frontmatter(overview)

    summary = scanner_result.get("summary", {})

    return {
        "name": "AI Trust & Safety Engine",
        "mission": "Build India's most accurate multilingual AI Voice Moderation Platform.",
        "type": "Trust & Safety Intelligence Platform (NOT a transcription tool)",
        "project_root": summary.get("project_root", ""),
        "detected_frameworks": summary.get("detected_frameworks", []),
        "total_python_files": summary.get("python_files_count", 0),
        "total_files": summary.get("total_files_scanned", 0),
        "has_dockerfile": summary.get("has_dockerfile", False),
        "has_systemd": summary.get("has_systemd", False),
        "knowledge_last_updated": meta.get("last_updated", "unknown"),
        "knowledge_status": meta.get("status", "unknown"),
    }


def _build_architecture(scanner_result: dict) -> dict:
    """Extract architecture context from knowledge base."""
    arch_content = _read_knowledge("architecture.md") or ""
    body = _strip_frontmatter(arch_content)

    # Extract the implementation status table (MODULE → status → file)
    module_status = _parse_markdown_table(body)

    # Extract the 6-layer model description
    layer_section = _extract_section(body, "6-Layer")

    return {
        "model": "6-Layer Intelligence Pipeline",
        "layers": [
            {"layer": 1, "name": "Audio Intelligence",      "responsibility": "Download, validate, VAD, format normalize"},
            {"layer": 2, "name": "Speech Intelligence",     "responsibility": "Whisper ASR, Pyannote diarization, speaker attribution"},
            {"layer": 3, "name": "Language Intelligence",   "responsibility": "Normalization, code-switching, transliteration, phonetics"},
            {"layer": 4, "name": "Compliance Intelligence", "responsibility": "Deterministic detection: PII, Threat, Abuse, Scam, Risk"},
            {"layer": 5, "name": "Reasoning Intelligence",  "responsibility": "LLM (Gemini) — explain and synthesize, never detect"},
            {"layer": 6, "name": "Business Intelligence",   "responsibility": "Alert, Analytics, Dashboard, Audit, Client delivery"},
        ],
        "critical_rule": (
            "Layer 4 DETECTS (deterministic). "
            "Layer 5 EXPLAINS (LLM). "
            "This boundary must NEVER be crossed."
        ),
        "module_implementation_status": module_status,
        "current_data_flow": (
            "POST /api/analyze-call → job created (202) → BackgroundTask → "
            "download → Whisper → Pyannote → violation_service → Gemini → "
            "email_alert → job COMPLETED"
        ),
        "api_prefix": "/api",
        "backend_port": 8001,
    }


def _build_features(progress_content: str) -> dict:
    """
    Parse progress.md into structured feature buckets.
    Returns implemented, in_progress, and pending lists.
    """
    if not progress_content:
        return {"implemented": [], "in_progress": [], "pending": [], "blockers": []}

    body = _strip_frontmatter(progress_content)

    # Parse checklist items
    checklist = _parse_checklist(body)

    # Extract numbered pending items (prioritized backlog)
    pending_section = _extract_section(body, "PENDING")
    numbered_pending = _parse_numbered_list(pending_section)

    # Extract blockers
    blockers_section = _extract_section(body, "KNOWN BLOCKERS")
    blockers = _parse_numbered_list(blockers_section)

    # Fallback: use plain - items in blockers section
    if not blockers:
        for line in blockers_section.splitlines():
            m = re.match(r"^\d+\.\s+\*\*([^*]+)\*\*\s*—\s*(.+)$", line.strip())
            if m:
                blockers.append(f"{m.group(1)}: {m.group(2)}")

    # Combine numbered pending with checklist pending
    all_pending = numbered_pending if numbered_pending else checklist["pending"]

    return {
        "implemented": checklist["done"],
        "in_progress": checklist["in_progress"],
        "pending": all_pending,
        "blockers": blockers,
        "counts": {
            "implemented": len(checklist["done"]),
            "in_progress": len(checklist["in_progress"]),
            "pending": len(all_pending),
            "blockers": len(blockers),
        },
    }


def _build_dependencies(content: str) -> list[dict]:
    """Parse dependencies.md into structured list."""
    if not content:
        return []
    body = _strip_frontmatter(content)
    rows = _parse_markdown_table(body)
    # Normalize column names
    normalized = []
    for row in rows:
        normalized.append({
            "package": row.get("package", row.get("`package`", "")),
            "version": row.get("version", row.get("version pinned", "")),
            "purpose": row.get("purpose", ""),
            "replaceable_with": row.get("replaceable with", ""),
        })
    return [r for r in normalized if r["package"]]


def _build_current_sprint(progress_content: str) -> dict:
    """Extract the current sprint from progress.md."""
    if not progress_content:
        return {}

    body = _strip_frontmatter(progress_content)
    in_progress_section = _extract_section(body, "IN PROGRESS")
    checklist = _parse_checklist(in_progress_section)

    # The sprint goal is the MCP implementation + intelligence modules
    return {
        "goal": "Complete MCP Server + Phase 1 Intelligence Modules",
        "active_items": checklist["pending"] or [
            "MCP server implementation (build_context module)"
        ],
        "next_critical_item": "Indian Number Intelligence module (OTP/phone detection in Indic languages)",
        "phase": "Phase 1: Enterprise Async SaaS",
    }


def _build_current_todo(progress_content: str) -> list[dict]:
    """
    Extract the prioritized TODO list from the pending backlog in progress.md.
    Returns items as {priority, item, category}.
    """
    if not progress_content:
        return []

    body = _strip_frontmatter(progress_content)
    pending_section = _extract_section(body, "PENDING")
    numbered_items = _parse_numbered_list(pending_section)

    todo = []
    for i, item in enumerate(numbered_items, start=1):
        # Parse "Item name — description" format
        parts = item.split(" — ", 1)
        todo.append({
            "priority": i,
            "item": parts[0].strip(),
            "detail": parts[1].strip() if len(parts) > 1 else "",
            "category": "Phase 1 Intelligence Module",
        })

    # Add infra items from the Infrastructure sub-section
    infra_section = _extract_section(pending_section, "Infrastructure")
    for line in infra_section.splitlines():
        if line.strip().startswith("- "):
            text = line.strip()[2:].strip()
            if text:
                todo.append({
                    "priority": len(todo) + 1,
                    "item": text,
                    "detail": "",
                    "category": "Infrastructure",
                })

    return todo


# ---------------------------------------------------------------------------
# AI-Ready Summary builder
# ---------------------------------------------------------------------------

def _build_ai_summary(context: dict, api_routes: list[dict]) -> str:
    """
    Generate a single formatted markdown string that any AI can use as
    a system prompt to immediately understand the full project state.
    """
    ps = context["project_summary"]
    arch = context["current_architecture"]
    features = context["features"]
    sprint = context["current_sprint"]
    issues = context["known_issues"]
    todo = context["current_todo"]

    lines = [
        "# AI Trust & Safety Engine — Engineering Context",
        "",
        "## What This Project Is",
        f"**Mission:** {ps['mission']}",
        f"**Type:** {ps['type']}",
        f"**Backend Port:** {arch['backend_port']} | **API Prefix:** {arch['api_prefix']}",
        f"**Stack:** {', '.join(ps['detected_frameworks'])}",
        "",
        "## Architecture — Critical Rule",
        f"> {arch['critical_rule']}",
        "",
        "## Current Pipeline Flow",
        f"`{arch['current_data_flow']}`",
        "",
        "## Live API Surface",
    ]

    if api_routes:
        for route in api_routes:
            lines.append(f"- `{route['method']:6} {route['path']}` → `{route['handler']}` ({route['file']}:{route['line']})")
    else:
        lines.append("- No routes discovered (run scan_project for live data)")

    lines += [
        "",
        "## What Is Already Built",
        f"({features['counts']['implemented']} items completed)",
    ]
    for item in features["implemented"][:15]:   # Top 15 to keep summary manageable
        lines.append(f"- ✅ {item}")
    if len(features["implemented"]) > 15:
        lines.append(f"- ... and {len(features['implemented']) - 15} more (see get_current_progress)")

    lines += ["", "## Current Sprint"]
    lines.append(f"**Goal:** {sprint['goal']}")
    lines.append(f"**Next critical item:** {sprint['next_critical_item']}")
    for item in sprint["active_items"]:
        lines.append(f"- 🔄 {item}")

    lines += ["", "## Priority TODO (Build This Next)"]
    for item in todo[:6]:
        lines.append(f"{item['priority']}. **{item['item']}** — {item['detail']}")

    if features["blockers"]:
        lines += ["", "## Active Blockers 🚨"]
        for b in features["blockers"]:
            lines.append(f"- ❌ {b}")

    lines += ["", "## Key Known Issues"]
    for issue in issues[:3]:
        lines.append(
            f"- **{issue['id']} [{issue['severity']}]** {issue['title']}: "
            f"{issue.get('workaround', 'See get_known_issues for workaround.')}"
        )
    if len(issues) > 3:
        lines.append(f"- ... {len(issues) - 3} more issues. Call `get_known_issues` for full list.")

    lines += [
        "",
        "---",
        "## Engineering Rules (Non-Negotiable)",
        "- P-07: LLM never performs detection. Layer 4 detects. Layer 5 explains.",
        "- P-03: Audio is never persisted. Always delete in finally block.",
        "- P-12: Business rules (thresholds, word lists) are config, not code.",
        "- All functions need type hints. All services use singleton pattern.",
        "- Commit style: `feat(scope): description` (small atomic commits).",
        "",
        "_Context generated by AI Trust & Safety Engine MCP Server._",
        "_For live project structure: call `scan_project()`. For full issues: call `get_known_issues()`._",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def handle(
    include_file_tree: bool = True,
    include_python_details: bool = False,
) -> dict:
    """
    Build a comprehensive, AI-ready engineering context for this project.

    Combines live scanner data with human-authored knowledge base content
    into a single unified response. Generates an `ai_ready_summary` that
    can be used directly as a system prompt in any AI assistant.

    Args:
        include_file_tree:      Include directory tree in output (default: True)
        include_python_details: Include per-file Python analysis (default: False)

    Returns:
        Full context dict with all 7 sections + ai_ready_summary.
    """
    build_start = datetime.now(timezone.utc)
    errors: list[str] = []

    # ------------------------------------------------------------------ #
    # Step 1: Live project scan (ground truth)                            #
    # ------------------------------------------------------------------ #
    scanner_result = {}
    try:
        scanner_result = _run_scanner()
    except Exception as e:
        errors.append(f"scanner_failed: {e}")

    api_routes = scanner_result.get("api_routes", [])

    # ------------------------------------------------------------------ #
    # Step 2: Read all knowledge files                                    #
    # ------------------------------------------------------------------ #
    progress_content = _read_knowledge("progress.md") or ""
    issues_content = _read_knowledge("known_issues.md") or ""
    deps_content = _read_knowledge("dependencies.md") or ""

    # ------------------------------------------------------------------ #
    # Step 3: Build each context section                                  #
    # ------------------------------------------------------------------ #
    try:
        project_summary = _build_project_summary(scanner_result)
    except Exception as e:
        project_summary = {"error": str(e)}
        errors.append(f"project_summary_failed: {e}")

    try:
        current_architecture = _build_architecture(scanner_result)
    except Exception as e:
        current_architecture = {"error": str(e)}
        errors.append(f"architecture_failed: {e}")

    try:
        features = _build_features(progress_content)
    except Exception as e:
        features = {"error": str(e)}
        errors.append(f"features_failed: {e}")

    try:
        dependencies = _build_dependencies(deps_content)
    except Exception as e:
        dependencies = []
        errors.append(f"dependencies_failed: {e}")

    try:
        current_sprint = _build_current_sprint(progress_content)
    except Exception as e:
        current_sprint = {"error": str(e)}
        errors.append(f"sprint_failed: {e}")

    try:
        known_issues = _parse_issues(issues_content)
    except Exception as e:
        known_issues = []
        errors.append(f"known_issues_failed: {e}")

    try:
        current_todo = _build_current_todo(progress_content)
    except Exception as e:
        current_todo = []
        errors.append(f"todo_failed: {e}")

    # ------------------------------------------------------------------ #
    # Step 4: Assemble context                                            #
    # ------------------------------------------------------------------ #
    context = {
        "project_summary":      project_summary,
        "current_architecture": current_architecture,
        "features":             features,
        "dependencies":         dependencies,
        "current_sprint":       current_sprint,
        "known_issues":         known_issues,
        "current_todo":         current_todo,
    }

    # ------------------------------------------------------------------ #
    # Step 5: Generate AI-ready summary                                   #
    # ------------------------------------------------------------------ #
    try:
        ai_ready_summary = _build_ai_summary(context, api_routes)
    except Exception as e:
        ai_ready_summary = f"[Summary generation failed: {e}]"
        errors.append(f"summary_failed: {e}")

    # ------------------------------------------------------------------ #
    # Step 6: Assemble final response                                     #
    # ------------------------------------------------------------------ #
    build_duration_ms = int(
        (datetime.now(timezone.utc) - build_start).total_seconds() * 1000
    )

    response = {
        "tool": "build_context",
        "generated_at": build_start.isoformat(),
        "build_duration_ms": build_duration_ms,
        "context": context,
        "ai_ready_summary": ai_ready_summary,
        "api_surface": api_routes,
    }

    if include_file_tree:
        response["directory_tree"] = scanner_result.get("directory_tree", {})

    if include_python_details:
        response["python_files"] = scanner_result.get("python_files", [])

    if errors:
        response["build_warnings"] = errors

    return response


# ---------------------------------------------------------------------------
# CLI — standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = handle(include_file_tree=False)

    print("=" * 70)
    print("CONTEXT BUILDER — AI-READY SUMMARY")
    print("=" * 70)
    print(result["ai_ready_summary"])

    ctx = result["context"]
    print("\n" + "=" * 70)
    print(f"Build time: {result['build_duration_ms']}ms")
    print(f"Implemented features: {ctx['features']['counts']['implemented']}")
    print(f"Pending TODO items:   {len(ctx['current_todo'])}")
    print(f"Known issues:         {len(ctx['known_issues'])}")
    print(f"Dependencies:         {len(ctx['dependencies'])}")
    if result.get("build_warnings"):
        print(f"\nWarnings: {result['build_warnings']}")
