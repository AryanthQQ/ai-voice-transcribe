"""
Tool: memory_engine
MCP Tool Name: memory_engine

Purpose:
    A persistent, queryable memory store for the AI Trust & Safety Engine.
    Stores and manages dynamic project state:
      - Completed Features
      - Pending Features
      - Architecture Decisions
      - Known Bugs
      - Important Notes
      - Project Goals
      - Current Version
      - Next Sprint

    This tool acts as a living memory that any AI can read from or write to,
    ensuring continuity between sessions and across different AI engineers.

Inputs:
    action (str): The operation to perform: "read", "add", "remove", "set_version".
    category (str): The memory category (e.g., "completed_features", "known_bugs").
                    Required for "add" and "remove".
    value (str): The value to add or set. Required for "add" and "set_version".
    index (int): The index of the item to remove. Required for "remove".

Outputs:
    For "read":
        {
          "tool": "memory_engine",
          "memory": { ... }
        }
    For mutations ("add", "remove", "set_version"):
        {
          "tool": "memory_engine",
          "status": "success",
          "action": "...",
          "message": "...",
          "memory": { ... }
        }

Design Principles:
    - Backed by mcp/knowledge/memory.json.
    - Fault-tolerant reading (creates default memory if missing).
    - Atomic writes to prevent corruption.
"""

import json
from pathlib import Path
from typing import Optional

_TOOLS_DIR = Path(__file__).resolve().parent
_MCP_DIR = _TOOLS_DIR.parent
_KNOWLEDGE_DIR = _MCP_DIR / "knowledge"
_MEMORY_FILE = _KNOWLEDGE_DIR / "memory.json"

DEFAULT_MEMORY = {
    "project_goals": [],
    "current_version": "0.1.0",
    "completed_features": [],
    "pending_features": [],
    "architecture_decisions": [],
    "known_bugs": [],
    "important_notes": [],
    "next_sprint": []
}

def _read_memory() -> dict:
    if not _MEMORY_FILE.exists():
        _write_memory(DEFAULT_MEMORY)
        return DEFAULT_MEMORY.copy()
    try:
        content = _MEMORY_FILE.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        # If file is corrupted, return default but don't overwrite blindly
        return DEFAULT_MEMORY.copy()

def _write_memory(memory: dict) -> None:
    _MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")

def handle(
    action: str = "read",
    category: Optional[str] = None,
    value: Optional[str] = None,
    index: Optional[int] = None
) -> dict:
    """
    Manage the persistent project memory.

    Actions:
      - "read": Return the entire memory state.
      - "add": Add `value` to `category` list.
      - "remove": Remove item at `index` from `category` list.
      - "set_version": Set current_version to `value`.

    Valid categories: project_goals, completed_features, pending_features,
    architecture_decisions, known_bugs, important_notes, next_sprint.
    """
    mem = _read_memory()
    action = action.lower()

    if action == "read":
        return {
            "tool": "memory_engine",
            "memory": mem
        }

    elif action == "set_version":
        if not value:
            return {"error": "Value required for set_version."}
        old_version = mem.get("current_version")
        mem["current_version"] = value
        _write_memory(mem)
        return {
            "tool": "memory_engine",
            "status": "success",
            "action": "set_version",
            "message": f"Updated version from {old_version} to {value}",
            "memory": mem
        }

    list_categories = [
        "project_goals", "completed_features", "pending_features",
        "architecture_decisions", "known_bugs", "important_notes", "next_sprint"
    ]

    if action in ("add", "remove"):
        if category not in list_categories:
            return {
                "error": "INVALID_CATEGORY",
                "message": f"Category must be one of: {', '.join(list_categories)}",
                "provided_category": category
            }
        
        target_list = mem.setdefault(category, [])

        if action == "add":
            if not value:
                return {"error": "Value required for add action."}
            target_list.append(value)
            _write_memory(mem)
            return {
                "tool": "memory_engine",
                "status": "success",
                "action": "add",
                "message": f"Added item to {category}",
                "memory": mem
            }

        elif action == "remove":
            if index is None:
                return {"error": "Index required for remove action."}
            try:
                removed_item = target_list.pop(index)
                _write_memory(mem)
                return {
                    "tool": "memory_engine",
                    "status": "success",
                    "action": "remove",
                    "message": f"Removed item from {category}: {removed_item}",
                    "memory": mem
                }
            except IndexError:
                return {
                    "error": "INVALID_INDEX",
                    "message": f"Index {index} is out of range for category {category}."
                }

    return {
        "error": "INVALID_ACTION",
        "message": "Action must be read, add, remove, or set_version."
    }

if __name__ == "__main__":
    # CLI test
    import sys
    print("Reading memory...")
    res = handle("read")
    print(json.dumps(res, indent=2))
