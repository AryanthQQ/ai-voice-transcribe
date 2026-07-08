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
    (See docstring inside execute() for details)
"""

import ast
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Set, Tuple

from mcp.tools.base import BaseTool

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------

MAX_READ_BYTES = 100_000   # 100 KB max per file read
MAX_TREE_DEPTH = 4         # Max directory recursion depth for tree view

# Directories that are always excluded from scanning
SKIP_DIRS: Set[str] = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "env",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
    ".next", ".nuxt", "coverage", "htmlcov", ".eggs", "eggs",
    ".tox", ".nox", "mcp",   # Exclude the MCP server itself
}

# Exact filenames (lowercased) to collect as config files
CONFIG_FILENAMES: Set[str] = {
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
README_FILENAMES: Set[str] = {
    "readme.md", "readme.txt", "readme.rst", "readme",
}

# Systemd unit file extensions
SYSTEMD_EXTENSIONS: Set[str] = {".service", ".socket", ".timer", ".mount", ".target"}

# FastAPI HTTP methods to detect in decorator analysis
HTTP_METHODS: Tuple[str, ...] = ("get", "post", "put", "patch", "delete", "options", "head")


class ProjectScanner(BaseTool):
    """
    Enterprise-grade Project Scanner.
    Extracts structure, AST metadata, and configs from the repository.
    """

    def _safe_read(self, path: Path, max_bytes: int = MAX_READ_BYTES) -> str:
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
            self.logger.warning(f"Permission denied reading {path}")
            return "[permission denied]"
        except OSError as e:
            self.logger.error(f"OS error reading {path}: {e}")
            return f"[read error: {e}]"

    def _should_skip(self, path: Path) -> bool:
        """Return True if this path is inside a skipped directory."""
        return any(part in SKIP_DIRS for part in path.parts)

    def _parse_python_file(self, filepath: Path, root: Path) -> Dict[str, Any]:
        """
        Parse a Python source file using the AST.
        """
        rel_path = str(filepath.relative_to(root))
        source = self._safe_read(filepath, max_bytes=MAX_READ_BYTES)

        result: Dict[str, Any] = {
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
            self.logger.warning(f"Syntax error parsing {rel_path}: {e}")
            return result
        except Exception as e:
            result["parse_error"] = str(e)
            self.logger.error(f"Unexpected error parsing {rel_path}: {e}")
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
                        decorator_str = (
                            ast.unparse(decorator)
                            if hasattr(ast, "unparse")
                            else ""
                        )
                        for method in HTTP_METHODS:
                            if f".{method}(" in decorator_str:
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
                                break
                    except Exception:
                        pass

        return result

    def _parse_requirements(self, filepath: Path) -> List[Dict[str, str]]:
        """
        Parse a requirements.txt-style file.
        """
        packages = []
        for raw_line in self._safe_read(filepath, max_bytes=20_000).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("-") or line.startswith("http"):
                continue
            m = re.match(r"^([A-Za-z0-9_\-\[\]\.]+)\s*([><=!~,\s].+)?$", line)
            if m:
                packages.append({
                    "package": m.group(1),
                    "version_spec": (m.group(2) or "").strip(),
                    "raw": line,
                })
        return packages

    def _build_tree(self, root: Path, current: Path, depth: int = 0) -> Dict[str, Any]:
        """
        Recursively build a depth-limited directory tree.
        """
        if depth > MAX_TREE_DEPTH:
            return {"_truncated": f"depth limit ({MAX_TREE_DEPTH}) reached"}

        result: Dict[str, Any] = {}
        try:
            entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            self.logger.warning(f"Permission denied listing {current}")
            return {"_error": "permission denied"}

        for entry in entries:
            if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                continue
            if entry.is_dir():
                result[entry.name + "/"] = self._build_tree(root, entry, depth + 1)
            elif entry.is_file():
                try:
                    size = entry.stat().st_size
                except OSError:
                    size = -1
                result[entry.name] = {"size_bytes": size}

        return result

    def _detect_frameworks(self, all_imports: Set[str], root: Path) -> List[str]:
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

        if (root / "frontend").exists():
            detected.append("React Frontend (frontend/)")
        if (root / "package.json").exists():
            detected.append("Node.js / npm")
        if (root / "frontend" / "tsconfig.json").exists() or (root / "tsconfig.json").exists():
            detected.append("TypeScript")

        return detected

    def execute(self, project_root: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Scan the entire repository and return comprehensive project metadata.
        """
        if project_root:
            root = Path(project_root).resolve()
        else:
            root = self.config.project_root

        if not root.exists() or not root.is_dir():
            self.logger.error(f"Project root does not exist: {root}")
            return {
                "tool": "scan_project",
                "error": "INVALID_ROOT",
                "message": f"Project root does not exist or is not a directory: {root}",
            }

        self.logger.info(f"Starting scan of project root: {root}")
        scan_start = datetime.now(timezone.utc)

        python_files: List[Path] = []
        config_files: Dict[str, str] = {}
        requirements_files: Dict[str, List[Dict[str, str]]] = {}
        dockerfiles: Dict[str, str] = {}
        systemd_units: Dict[str, str] = {}
        readme_content: Optional[str] = None
        total_scanned = 0

        for filepath in sorted(root.rglob("*")):
            if not filepath.is_file():
                continue
            if self._should_skip(filepath):
                continue

            total_scanned += 1
            name_lower = filepath.name.lower()
            ext_lower = filepath.suffix.lower()

            try:
                rel = str(filepath.relative_to(root))
            except ValueError:
                continue

            if ext_lower == ".py":
                python_files.append(filepath)

            if name_lower in README_FILENAMES and readme_content is None:
                readme_content = self._safe_read(filepath, max_bytes=30_000)

            if name_lower in CONFIG_FILENAMES:
                config_files[rel] = self._safe_read(filepath, max_bytes=15_000)

            if name_lower.startswith("requirements") and ext_lower == ".txt":
                requirements_files[rel] = self._parse_requirements(filepath)

            if name_lower in ("dockerfile", "dockerfile.prod", "dockerfile.dev",
                               "dockerfile.staging", "docker-compose.yml",
                               "docker-compose.yaml", "docker-compose.prod.yml",
                               "docker-compose.prod.yaml"):
                dockerfiles[rel] = self._safe_read(filepath, max_bytes=15_000)

            if ext_lower in SYSTEMD_EXTENSIONS:
                systemd_units[rel] = self._safe_read(filepath, max_bytes=10_000)

        parsed_python: List[Dict[str, Any]] = []
        all_routes: List[Dict[str, Any]] = []
        all_imports: Set[str] = set()
        all_classes: List[Dict[str, Any]] = []

        for pyfile in python_files:
            parsed = self._parse_python_file(pyfile, root)
            parsed_python.append(parsed)
            all_routes.extend(parsed["routes"])
            all_imports.update(parsed["imports"])
            for cls in parsed["classes"]:
                all_classes.append({"file": parsed["path"], **cls})

        directory_tree = self._build_tree(root, root)
        detected_frameworks = self._detect_frameworks(all_imports, root)

        scan_duration_ms = int(
            (datetime.now(timezone.utc) - scan_start).total_seconds() * 1000
        )
        
        self.logger.info(f"Scan completed in {scan_duration_ms}ms. Total files: {total_scanned}")

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
