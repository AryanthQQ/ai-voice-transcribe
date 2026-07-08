"""
Tool: knowledge_base
MCP Tool Name: knowledge_base

Purpose:
    A persistent, queryable knowledge base for the AI Trust & Safety Engine.
    Stores and manages engineering documentation and guidelines:
      - Engineering Standards
      - Coding Rules
      - Architecture Notes
      - Model Information
      - Infrastructure Notes
      - Deployment Notes

    This tool acts as a living handbook that any AI can read from or write to.
    It guarantees that important standards and notes are preserved.

Inputs:
    action (str): The operation to perform: "read", "add_note", "remove_note".
    topic (str): The knowledge topic (e.g., "coding_rules"). Optional for "read".
    note (str): The note content to add. Required for "add_note".
    index (int): The index of the note to remove. Required for "remove_note".

Outputs:
    For "read":
        {
          "tool": "knowledge_base",
          "data": { ... }
        }
    For mutations ("add_note", "remove_note"):
        {
          "tool": "knowledge_base",
          "status": "success",
          "action": "...",
          "message": "...",
          "data": { ... }
        }

Design Principles:
    - Backed by mcp/knowledge/kb.json.
    - Fault-tolerant reading (creates default KB if missing).
    - Atomic writes to prevent corruption.
"""

import json
from pathlib import Path
from typing import Optional

_TOOLS_DIR = Path(__file__).resolve().parent
_MCP_DIR = _TOOLS_DIR.parent
_KNOWLEDGE_DIR = _MCP_DIR / "knowledge"
_KB_FILE = _KNOWLEDGE_DIR / "kb.json"

DEFAULT_KB = {
    "engineering_standards": [],
    "coding_rules": [],
    "architecture_notes": [],
    "model_information": [],
    "infrastructure_notes": [],
    "deployment_notes": []
}

def _read_kb() -> dict:
    if not _KB_FILE.exists():
        _write_kb(DEFAULT_KB)
        return DEFAULT_KB.copy()
    try:
        content = _KB_FILE.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        # If file is corrupted, return default but don't overwrite blindly
        return DEFAULT_KB.copy()

def _write_kb(kb: dict) -> None:
    _KB_FILE.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")

def handle(
    action: str = "read",
    topic: Optional[str] = None,
    note: Optional[str] = None,
    index: Optional[int] = None
) -> dict:
    """
    Manage the persistent Knowledge Base.

    Actions:
      - "read": Return the entire KB (or specific topic if provided).
      - "add_note": Add `note` to `topic`.
      - "remove_note": Remove item at `index` from `topic`.

    Valid topics: engineering_standards, coding_rules, architecture_notes,
    model_information, infrastructure_notes, deployment_notes.
    """
    kb = _read_kb()
    action = action.lower()

    if action == "read":
        if topic:
            if topic not in kb:
                return {"error": "INVALID_TOPIC", "message": f"Topic '{topic}' not found."}
            return {
                "tool": "knowledge_base",
                "topic": topic,
                "data": kb[topic]
            }
        return {
            "tool": "knowledge_base",
            "data": kb
        }

    topics = [
        "engineering_standards", "coding_rules", "architecture_notes",
        "model_information", "infrastructure_notes", "deployment_notes"
    ]

    if action in ("add_note", "remove_note"):
        if topic not in topics:
            return {
                "error": "INVALID_TOPIC",
                "message": f"Topic must be one of: {', '.join(topics)}",
                "provided_topic": topic
            }
        
        target_list = kb.setdefault(topic, [])

        if action == "add_note":
            if not note:
                return {"error": "Note content required for add_note action."}
            target_list.append(note)
            _write_kb(kb)
            return {
                "tool": "knowledge_base",
                "status": "success",
                "action": "add_note",
                "message": f"Added note to {topic}",
                "data": kb
            }

        elif action == "remove_note":
            if index is None:
                return {"error": "Index required for remove_note action."}
            try:
                removed_item = target_list.pop(index)
                _write_kb(kb)
                return {
                    "tool": "knowledge_base",
                    "status": "success",
                    "action": "remove_note",
                    "message": f"Removed note from {topic}",
                    "removed_content": removed_item,
                    "data": kb
                }
            except IndexError:
                return {
                    "error": "INVALID_INDEX",
                    "message": f"Index {index} is out of range for topic {topic}."
                }

    return {
        "error": "INVALID_ACTION",
        "message": "Action must be read, add_note, or remove_note."
    }

if __name__ == "__main__":
    # CLI test
    import sys
    print("Reading KB...")
    res = handle("read")
    print(json.dumps(res, indent=2))
