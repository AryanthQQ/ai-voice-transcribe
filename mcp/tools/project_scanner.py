"""
Tool: scan_project
MCP Tool Name: scan_project

Purpose:
    Scan the entire repository and build rich project metadata from what
    actually exists on disk — not from the knowledge base.

    This is the PRIMARY tool any AI should call first when joining a session.
    It gives a ground-truth picture of the project: structure, Python modules,
    API endpoints, configs, requirements, Docker, and systemd units.

Inputs:
    project_root (str, optional): Absolute path to the repository root.
                                  Defaults to the repo root (2 levels above this file).

Outputs:
    {
      "tool": "scan_project",
      "summary": {
        "project_root": str,
        "scanned_at": ISO8601,
        "scan_duration_ms": int,
        "total_files_scanned": int,
        "python_files_count": int,
        "api_routes_discovered": int,
        "detected_frameworks": [...],
        "has_dockerfile": bool,
        "has_systemd": bool,
        ...
      },
      "directory_tree": {...},   # nested dict, depth-limited to 4 levels
      "api_routes": [...],       # all FastAPI routes discovered via AST
      "classes": [...],          # all Python classes with methods
      "python_files": [...],     # per-file: imports, classes, functions, routes
      "config_files": {...},     # file path -> content (env.example, pyproject, etc.)
      "requirements": {...},     # file path -> [{package, version_spec}]
      "dockerfiles": {...},      # file path -> content
      "systemd_units": {...},    # file path -> content
      "readme": str | null       # content of the first README found
    }

Design Principles:
    - Stdlib only — zero external dependencies.
    - AST-based Python parsing for accuracy (not regex).
    - All reads are fault-tolerant: errors are captured, not raised.
    - Binary files are detected and skipped.
    - Max file read size: 100KB (configurable via MAX_READ_BYTES).
    - Max tree depth: 4 levels (configurable via MAX_TREE_DEPTH).
"""

import ast
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_READ_BYTES = 100_000   # 100 KB max per file read
MAX_TREE_DEPTH = 4         # Max directory recursion depth for tree view

# Directories that are always excluded from scanning
SKIP_DIRS: set[str] = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "env",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
    ".next", ".nuxt", "coverage", "htmlcov", ".eggs", "eggs",
    ".tox", ".nox", "mcp",   # Exclude the MCP server itself
}

# Exact filenames (lowercased) to collect as config files
CONFIG_FILENAMES: set[str] = {
    ".env.example", ".env.template", ".env.sample",
    "pyproject.toml", "setup.cfg", "setup.py",
    "tsconfig.json", "tsconfig.node.json",
    "vite.config.ts", "vite.config.js",
    "package.json",
    ".gitignore", ".dockerignore",
    "docker-compose.yml", "docker-compose.yaml",
    "docker-compose.prod.yml", "docker-compose.prod.yaml",
    "nginx.conf", "nginx.conf.d",
    "Makefile", "makefile",
    "supervisord.conf",
}

# README filenames (lowercased)
README_FILENAMES: set[str] = {
    "readme.md", "readme.txt", "readme.rst", "readme",
}

# Systemd unit file extensions
SYSTEMD_EXTENSIONS: set[str] = {".service", ".socket", ".timer", ".mount", ".target"}

# FastAPI HTTP methods to detect in decorator analysis
HTTP_METHODS: tuple[str, ...] = ("get", "post", "put", "patch", "delete", "options", "head")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_read(path: Path, max_bytes: int = MAX_READ_BYTES) -> str:
    """
    Read a file safely. Returns error string instead of raising.
    Detects binary files by checking for null bytes in the first 1 KB.
    """
    try:
        raw = path.read_bytes()
        # Binary file detection
        if b"\x00" in raw[:1024]:
            return f"[binary file — {len(raw):,} bytes, skipped]"
        return raw[:max_bytes].decode("utf-8", errors="replace")
    except PermissionError:
        return "[permission denied]"
    except OSError as e:
        return f"[read error: {e}]"


def _should_skip(path: Path) -> bool:
    """Return True if this path is inside a skipped directory."""
    return any(part in SKIP_DIRS for part in path.parts)


def _parse_python_file(filepath: Path, root: Path) -> dict:
    """
    Parse a Python source file using the AST.

    Extracts:
      - Import statements (module names)
      - Class definitions (name, line, methods)
      - Function / async function definitions (name, line, is_async)
      - FastAPI / APIRouter route decorators (method, path, handler, line)

    Returns a dict with relative path and all extracted symbols.
    """
    rel_path = str(filepath.relative_to(root))
    source = _safe_read(filepath, max_bytes=MAX_READ_BYTES)

    result: dict = {
        "path": rel_path,
        "size_bytes": filepath.stat().st_size,
        "imports": [],
        "classes": [],
        "functions": [],
        "routes": [],
        "parse_error": None,
    }

    if source.startswith("["):  # Error string from _safe_read
        result["parse_error"] = source
        return result

    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as e:
        result["parse_error"] = f"SyntaxError at line {e.lineno}: {e.msg}"
        return result
    except Exception as e:
        result["parse_error"] = str(e)
        return result

    # Walk once, collect everything
    for node in ast.walk(tree):

        # --- Imports ---
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                result["imports"].append(f"{module}.{alias.name}" if module else alias.name)

        # --- Classes ---
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name
                for n in ast.walk(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n is not node
            ]
            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "methods": methods,
            })

        # --- Functions and FastAPI routes ---
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn_entry = {
                "name": node.name,
                "line": node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
            result["functions"].append(fn_entry)

            # Inspect decorators for FastAPI route patterns
            for decorator in node.decorator_list:
                try:
                    # Unparse the decorator to a string for analysis
                    decorator_str = (
                        ast.unparse(decorator)
                        if hasattr(ast, "unparse")      # Python 3.9+
                        else ""
                    )
                    for method in HTTP_METHODS:
                        if f".{method}(" in decorator_str:
                            # Try to extract the path argument
                            path_val = ""
                            if isinstance(decorator, ast.Call) and decorator.args:
                                first_arg = decorator.args[0]
                                if isinstance(first_arg, ast.Constant):
                                    path_val = str(first_arg.value)
                            result["routes"].append({
                                "method": method.upper(),
                                "path": path_val,
                                "handler": node.name,
                                "line": node.lineno,
                                "file": rel_path,
                            })
                            break   # Only record the first matching method
                except Exception:
                    pass    # Decorator parsing is best-effort

    return result


def _parse_requirements(filepath: Path) -> list[dict]:
    """
    Parse a requirements.txt-style file.
    Returns list of {package, version_spec, raw_line}.
    Skips comments, blank lines, and -r/-c directives.
    """
    packages = []
    for raw_line in _safe_read(filepath, max_bytes=20_000).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-") or line.startswith("http"):
            continue
        # Match package name and optional version specifier
        m = re.match(r"^([A-Za-z0-9_\-\[\]\.]+)\s*([><=!~,\s].+)?$", line)
        if m:
            packages.append({
                "package": m.group(1),
                "version_spec": (m.group(2) or "").strip(),
                "raw": line,
            })
    return packages


def _build_tree(root: Path, current: Path, depth: int = 0) -> dict:
    """
    Recursively build a depth-limited directory tree.
    Hidden files and SKIP_DIRS directories are excluded.
    """
    if depth > MAX_TREE_DEPTH:
        return {"_truncated": f"depth limit ({MAX_TREE_DEPTH}) reached"}

    result: dict = {}
    try:
        entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return {"_error": "permission denied"}

    for entry in entries:
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if entry.is_dir():
            result[entry.name + "/"] = _build_tree(root, entry, depth + 1)
        elif entry.is_file():
            try:
                size = entry.stat().st_size
            except OSError:
                size = -1
            result[entry.name] = {"size_bytes": size}

    return result


def _detect_frameworks(all_imports: set[str], root: Path) -> list[str]:
    """Detect which frameworks and technologies are in use."""
    detected = []
    import_str = " ".join(all_imports).lower()

    checks = [
        ("fastapi", "FastAPI"),
        ("flask", "Flask"),
        ("django", "Django"),
        ("faster_whisper", "faster-whisper (Whisper ASR)"),
        ("pyannote", "Pyannote (Speaker Diarization)"),
        ("google.genai", "Google GenAI SDK"),
        ("google.cloud.aiplatform", "Vertex AI"),
        ("torch", "PyTorch"),
        ("transformers", "HuggingFace Transformers"),
        ("librosa", "Librosa (Audio)"),
        ("pydantic", "Pydantic"),
        ("sqlalchemy", "SQLAlchemy"),
        ("redis", "Redis"),
    ]

    for keyword, label in checks:
        if keyword in import_str:
            detected.append(label)

    # File-based detection (no import needed)
    if (root / "frontend").exists():
        detected.append("React Frontend (frontend/)")
    if (root / "package.json").exists():
        detected.append("Node.js / npm")
    if (root / "frontend" / "tsconfig.json").exists() or (root / "tsconfig.json").exists():
        detected.append("TypeScript")

    return detected


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def handle(project_root: Optional[str] = None) -> dict:
    """
    Scan the entire repository and return comprehensive project metadata.

    This function reads actual files from disk. It is the ground-truth
    scanner — not derived from the knowledge base.

    Args:
        project_root: Optional absolute path to the repository root.
                      Defaults to the repository root (2 levels above this file).

    Returns:
        Structured dict with summary, directory tree, Python analysis,
        config files, requirements, Docker, systemd, and README.
    """
    # --- Resolve root ---
    if project_root:
        root = Path(project_root).resolve()
    else:
        # mcp/tools/project_scanner.py  -> parents[0] = mcp/tools -> parents[1] = mcp -> parents[2] = repo root
        root = Path(__file__).resolve().parents[2]

    if not root.exists() or not root.is_dir():
        return {
            "tool": "scan_project",
            "error": "INVALID_ROOT",
            "message": f"Project root does not exist or is not a directory: {root}",
        }

    scan_start = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ #
    # Phase 1: Walk all files, categorize them                           #
    # ------------------------------------------------------------------ #
    python_files: list[Path] = []
    config_files: dict[str, str] = {}
    requirements_files: dict[str, list[dict]] = {}
    dockerfiles: dict[str, str] = {}
    systemd_units: dict[str, str] = {}
    readme_content: Optional[str] = None
    total_scanned = 0

    for filepath in sorted(root.rglob("*")):
        if not filepath.is_file():
            continue
        if _should_skip(filepath):
            continue

        total_scanned += 1
        name_lower = filepath.name.lower()
        ext_lower = filepath.suffix.lower()

        try:
            rel = str(filepath.relative_to(root))
        except ValueError:
            continue

        # Python source
        if ext_lower == ".py":
            python_files.append(filepath)

        # README (first one found wins)
        if name_lower in README_FILENAMES and readme_content is None:
            readme_content = _safe_read(filepath, max_bytes=30_000)

        # Config files
        if name_lower in CONFIG_FILENAMES:
            config_files[rel] = _safe_read(filepath, max_bytes=15_000)

        # Requirements
        if name_lower.startswith("requirements") and ext_lower == ".txt":
            requirements_files[rel] = _parse_requirements(filepath)

        # Docker
        if name_lower in ("dockerfile", "dockerfile.prod", "dockerfile.dev",
                           "dockerfile.staging", "docker-compose.yml",
                           "docker-compose.yaml", "docker-compose.prod.yml",
                           "docker-compose.prod.yaml"):
            dockerfiles[rel] = _safe_read(filepath, max_bytes=15_000)

        # Systemd units
        if ext_lower in SYSTEMD_EXTENSIONS:
            systemd_units[rel] = _safe_read(filepath, max_bytes=10_000)

    # ------------------------------------------------------------------ #
    # Phase 2: AST-parse all Python files                                #
    # ------------------------------------------------------------------ #
    parsed_python: list[dict] = []
    all_routes: list[dict] = []
    all_imports: set[str] = set()
    all_classes: list[dict] = []

    for pyfile in python_files:
        parsed = _parse_python_file(pyfile, root)
        parsed_python.append(parsed)
        all_routes.extend(parsed["routes"])
        all_imports.update(parsed["imports"])
        for cls in parsed["classes"]:
            all_classes.append({"file": parsed["path"], **cls})

    # ------------------------------------------------------------------ #
    # Phase 3: Build directory tree                                       #
    # ------------------------------------------------------------------ #
    directory_tree = _build_tree(root, root)

    # ------------------------------------------------------------------ #
    # Phase 4: Detect frameworks and build summary                       #
    # ------------------------------------------------------------------ #
    detected_frameworks = _detect_frameworks(all_imports, root)

    scan_duration_ms = int(
        (datetime.now(timezone.utc) - scan_start).total_seconds() * 1000
    )

    summary = {
        "project_root": str(root),
        "scanned_at": scan_start.isoformat(),
        "scan_duration_ms": scan_duration_ms,
        "total_files_scanned": total_scanned,
        "python_files_count": len(python_files),
        "config_files_count": len(config_files),
        "requirements_files": list(requirements_files.keys()),
        "api_routes_discovered": len(all_routes),
        "classes_discovered": len(all_classes),
        "has_dockerfile": any(
            "dockerfile" in k.lower() and "compose" not in k.lower()
            for k in dockerfiles
        ),
        "has_docker_compose": any("docker-compose" in k for k in dockerfiles),
        "has_systemd": len(systemd_units) > 0,
        "has_readme": readme_content is not None,
        "detected_frameworks": detected_frameworks,
    }

    return {
        "tool": "scan_project",
        "summary": summary,
        "directory_tree": directory_tree,
        "api_routes": all_routes,
        "classes": all_classes,
        "python_files": parsed_python,
        "config_files": config_files,
        "requirements": requirements_files,
        "dockerfiles": dockerfiles,
        "systemd_units": systemd_units,
        "readme": readme_content,
    }


# ---------------------------------------------------------------------------
# CLI — run standalone for local testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    root_arg = sys.argv[1] if len(sys.argv) > 1 else None
    result = handle(root_arg)

    # Pretty-print summary only in CLI mode (full output would be huge)
    print("=" * 70)
    print("PROJECT SCANNER RESULT")
    print("=" * 70)
    print(json.dumps(result["summary"], indent=2))
    print()
    print(f"API Routes ({len(result['api_routes'])}):")
    for route in result["api_routes"]:
        print(f"  {route['method']:7} {route['path']:40} -> {route['handler']} ({route['file']}:{route['line']})")
    print()
    print(f"Config files ({len(result['config_files'])}):")
    for f in result["config_files"]:
        print(f"  {f}")
    print()
    print(f"Requirements files ({len(result['requirements'])}):")
    for f, pkgs in result["requirements"].items():
        print(f"  {f}: {len(pkgs)} packages")
    if result["systemd_units"]:
        print(f"\nSystemd units: {list(result['systemd_units'].keys())}")
    if result["dockerfiles"]:
        print(f"\nDocker files: {list(result['dockerfiles'].keys())}")
