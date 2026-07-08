"""
Tool: get_ai_context
MCP Tool Name: get_ai_context

Purpose:
    The ultimate machine-readable Context API for AI agents.
    It aggregates the outputs of the Project Scanner, Memory Engine, 
    and Knowledge Base into a single, structured JSON payload.

    Calling this ONE tool provides a complete, 360-degree view of the project:
      1. What exists on disk (Scanner)
      2. What is planned/completed (Memory)
      3. What the rules are (Knowledge Base)

Inputs:
    include_file_tree (bool): Include the full directory tree. Default True.

Outputs:
    {
      "tool": "get_ai_context",
      "timestamp": ISO8601,
      "project_disk_state": { ... scanner output ... },
      "project_memory_state": { ... memory output ... },
      "project_knowledge_base": { ... kb output ... }
    }
"""

from datetime import datetime, timezone
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_MCP_DIR = _TOOLS_DIR.parent

if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))

from tools.project_scanner import handle as _run_scanner
from tools.memory_engine import handle as _run_memory
from tools.knowledge_base import handle as _run_kb

def handle(include_file_tree: bool = True) -> dict:
    """
    Returns the complete structured AI context.
    """
    # 1. Get Live Disk State
    scanner_result = _run_scanner()
    if not include_file_tree and "directory_tree" in scanner_result:
        del scanner_result["directory_tree"]
        
    # Remove large raw content fields from scanner to keep JSON lightweight
    if "dockerfiles" in scanner_result: del scanner_result["dockerfiles"]
    if "systemd_units" in scanner_result: del scanner_result["systemd_units"]
    if "config_files" in scanner_result: del scanner_result["config_files"]
    if "readme" in scanner_result: del scanner_result["readme"]
    if "python_files" in scanner_result: del scanner_result["python_files"]

    # 2. Get Memory State
    memory_result = _run_memory(action="read").get("memory", {})

    # 3. Get Knowledge Base
    kb_result = _run_kb(action="read").get("data", {})

    return {
        "tool": "get_ai_context",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_disk_state": scanner_result,
        "project_memory_state": memory_result,
        "project_knowledge_base": kb_result
    }

if __name__ == "__main__":
    import json
    print(json.dumps(handle(include_file_tree=False), indent=2))
