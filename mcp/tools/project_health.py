"""
Tool: get_project_health
MCP Tool Name: get_project_health

Purpose:
    Diagnose the health of the project codebase dynamically.
    It tracks:
      - Missing standard files (README, .env templates)
      - Broken internal imports (Python modules that don't exist)
      - Duplicate files/logic (e.g. backend/ vs python_backend/)
      - Large files that should probably be ignored or chunked
      - Potential unused Python files
      - Project Statistics

Inputs:
    (See docstring inside execute() for details)
"""

import ast
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Set

from mcp.tools.base import BaseTool

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------
SKIP_DIRS: Set[str] = {".git", "__pycache__", "node_modules", "venv", ".venv", ".next", "dist", "build"}
ENTRY_POINTS: Set[str] = {"main.py", "app.py", "worker.py", "run.py", "manage.py", "setup.py"}

class ProjectHealth(BaseTool):
    """
    Enterprise-grade Project Health Diagnostic Tool.
    Analyzes ASTs and filesystem to detect technical debt and broken imports.
    """

    def _should_skip(self, path: Path) -> bool:
        """Return True if this path is inside a skipped directory."""
        return any(part in SKIP_DIRS for part in path.parts)

    def _get_internal_module_path(self, base_dir: Path, module_name: str) -> Optional[Path]:
        """Attempt to resolve a python module name (e.g., 'app.services.x') to a file path."""
        parts = module_name.split(".")
        
        # Try as a file: app/services/x.py
        file_path = base_dir.joinpath(*parts).with_suffix(".py")
        if file_path.exists():
            return file_path
            
        # Try as a package: app/services/x/__init__.py
        pkg_path = base_dir.joinpath(*parts) / "__init__.py"
        if pkg_path.exists():
            return pkg_path
            
        return None

    def execute(self, project_root: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the project health diagnostics.
        """
        if project_root:
            root = Path(project_root).resolve()
        else:
            root = self.config.project_root

        self.logger.info(f"Starting Project Health scan on {root}")
        start_time = datetime.now(timezone.utc)
        
        # Diagnostics buckets
        missing_files: List[str] = []
        broken_imports: List[str] = []
        dependency_problems: List[str] = []
        unused_files: List[str] = []
        duplicate_logic: List[str] = []
        large_files: List[str] = []
        
        # Statistics counters
        stats = {
            "total_files": 0,
            "total_size_mb": 0.0,
            "python_files": 0,
            "ts_js_files": 0,
            "json_files": 0
        }
        
        # Check standard missing files
        expected_files = ["README.md", ".gitignore", ".env.example"]
        for ef in expected_files:
            # Check case-insensitively for README
            if "readme" in ef.lower():
                if not any(f.name.lower().startswith("readme") for f in root.iterdir() if f.is_file()):
                    missing_files.append("README file is missing from the project root.")
            else:
                if not (root / ef).exists():
                    missing_files.append(f"{ef} is missing from the project root.")
                    
        # File iteration state
        py_files: List[Path] = []
        file_names: Dict[str, List[Path]] = defaultdict(list)
        total_bytes = 0
        
        for filepath in root.rglob("*"):
            if not filepath.is_file() or self._should_skip(filepath):
                continue
                
            stats["total_files"] += 1
            size = filepath.stat().st_size
            total_bytes += size
            
            if size > self.config.large_file_threshold_bytes:
                rel = str(filepath.relative_to(root))
                large_files.append(f"{rel} ({size / 1024 / 1024:.2f} MB)")
                
            ext = filepath.suffix.lower()
            if ext == ".py":
                stats["python_files"] += 1
                py_files.append(filepath)
                # Exclude mcp folder from duplicate logic check to focus on backend/frontend
                if "mcp" not in filepath.parts:
                    file_names[filepath.name].append(filepath)
            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                stats["ts_js_files"] += 1
            elif ext == ".json":
                stats["json_files"] += 1
                
        stats["total_size_mb"] = round(total_bytes / (1024 * 1024), 2)
        
        # Check for Duplicate Logic (Files with the exact same name in different top-level dirs)
        for name, paths in file_names.items():
            if len(paths) > 1 and name != "__init__.py":
                # Are they in different major directories?
                top_levels = {p.relative_to(root).parts[0] for p in paths if len(p.relative_to(root).parts) > 1}
                if len(top_levels) > 1:
                    duplicate_logic.append(
                        f"Duplicate filename '{name}' found across distinct top-level directories: " + 
                        ", ".join([str(p.relative_to(root)) for p in paths])
                    )
                    
        # Dependency problems
        backend_reqs = root / "backend" / "requirements.txt"
        if not backend_reqs.exists():
            dependency_problems.append("backend/requirements.txt is missing.")
            
        # Analyze Python imports (Broken Imports & Unused Files)
        imported_modules: Set[str] = set()
        internal_namespaces = {"app", "services", "api", "core", "models", "utils"}
        
        for py_file in py_files:
            try:
                rel_path = py_file.relative_to(root)
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(rel_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            base_module = node.module.split(".")[0]
                            imported_modules.add(base_module)
                            
                            # Check internal broken imports for 'app.*' namespace inside backend/
                            if "backend" in py_file.parts and base_module in internal_namespaces:
                                backend_dir = root / "backend"
                                resolved = self._get_internal_module_path(backend_dir, node.module)
                                if not resolved:
                                    broken_imports.append(f"Broken import in {rel_path}: 'from {node.module} import ...'")
                                    
            except SyntaxError as e:
                self.logger.warning(f"SyntaxError in {py_file.relative_to(root)}: {e.msg} at line {e.lineno}")
                broken_imports.append(f"SyntaxError in {py_file.relative_to(root)}: {e.msg} at line {e.lineno}")
            except Exception as e:
                self.logger.error(f"Error parsing {py_file}: {e}")
                
        # Unused internal files heuristic
        for py_file in py_files:
            if "backend" in py_file.parts and "mcp" not in py_file.parts:
                stem = py_file.stem
                if stem not in ENTRY_POINTS and stem != "__init__":
                    if stem not in imported_modules:
                        if "routes" not in py_file.parts:
                            unused_files.append(f"Potential unused file: {py_file.relative_to(root)}")
                            
        # Calculate Health Score (0-100)
        score = 100
        score -= len(missing_files) * 5
        score -= len(broken_imports) * 10
        score -= len(dependency_problems) * 10
        score -= len(duplicate_logic) * 8
        score -= len(large_files) * 2
        score = max(0, score)

        self.logger.info(f"Project Health scan complete. Score: {score}/100")

        return {
            "tool": "get_project_health",
            "timestamp": start_time.isoformat(),
            "health_score": score,
            "diagnostics": {
                "missing_files": missing_files,
                "broken_imports": broken_imports,
                "dependency_problems": dependency_problems,
                "duplicate_logic": duplicate_logic,
                "large_files": large_files,
                "potential_unused_files": unused_files[:10], # Limit noise
            },
            "project_statistics": stats
        }
