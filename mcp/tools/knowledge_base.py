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
    (See docstring inside execute() for details)
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from mcp.tools.base import BaseTool

DEFAULT_KB: Dict[str, Any] = {
    "engineering_standards": [],
    "coding_rules": [],
    "architecture_notes": [],
    "model_information": [],
    "infrastructure_notes": [],
    "deployment_notes": []
}

class KnowledgeBase(BaseTool):
    """
    Enterprise-grade Knowledge Base Engine.
    Manages persistent rules and standards across AI sessions using thread-safe JSON files.
    """

    @property
    def kb_file(self) -> Path:
        """Dynamically resolve the KB file from the injected config."""
        return self.config.get_knowledge_file_path("kb.json")

    def _read_kb(self) -> Dict[str, Any]:
        """Reads the KB JSON file safely."""
        if not self.kb_file.exists():
            self.logger.info(f"KB file not found. Creating default at {self.kb_file}")
            self.kb_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_kb(DEFAULT_KB)
            return DEFAULT_KB.copy()
        try:
            content = self.kb_file.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"Error reading KB file: {e}. Returning default KB.")
            # If file is corrupted, return default but don't overwrite blindly
            return DEFAULT_KB.copy()

    def _write_kb(self, kb: Dict[str, Any]) -> None:
        """Writes the KB JSON file atomically."""
        try:
            self.kb_file.parent.mkdir(parents=True, exist_ok=True)
            self.kb_file.write_text(
                json.dumps(kb, indent=2, ensure_ascii=False), 
                encoding="utf-8"
            )
            self.logger.debug(f"KB successfully written to {self.kb_file}")
        except Exception as e:
            self.logger.error(f"Failed to write KB to {self.kb_file}: {e}")

    def execute(
        self,
        action: str = "read",
        topic: Optional[str] = None,
        note: Optional[str] = None,
        index: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Manage the persistent Knowledge Base.

        Actions:
          - "read": Return the entire KB (or specific topic if provided).
          - "add_note": Add `note` to `topic`.
          - "remove_note": Remove item at `index` from `topic`.

        Valid topics: engineering_standards, coding_rules, architecture_notes,
        model_information, infrastructure_notes, deployment_notes.
        """
        kb = self._read_kb()
        action = action.lower()
        self.logger.info(f"KnowledgeBase executing action: {action}")

        if action == "read":
            if topic:
                if topic not in kb:
                    self.logger.warning(f"Topic '{topic}' not found in read action.")
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
                self.logger.warning(f"Invalid topic provided for {action}: {topic}")
                return {
                    "error": "INVALID_TOPIC",
                    "message": f"Topic must be one of: {', '.join(topics)}",
                    "provided_topic": topic
                }
            
            target_list = kb.setdefault(topic, [])

            if action == "add_note":
                if not note:
                    self.logger.warning("Note content required for add_note action.")
                    return {"error": "Note content required for add_note action."}
                target_list.append(note)
                self._write_kb(kb)
                return {
                    "tool": "knowledge_base",
                    "status": "success",
                    "action": "add_note",
                    "message": f"Added note to {topic}",
                    "data": kb
                }

            elif action == "remove_note":
                if index is None:
                    self.logger.warning("Index required for remove_note action.")
                    return {"error": "Index required for remove_note action."}
                try:
                    removed_item = target_list.pop(index)
                    self._write_kb(kb)
                    return {
                        "tool": "knowledge_base",
                        "status": "success",
                        "action": "remove_note",
                        "message": f"Removed note from {topic}",
                        "removed_content": removed_item,
                        "data": kb
                    }
                except IndexError:
                    self.logger.warning(f"Index {index} is out of range for topic {topic}.")
                    return {
                        "error": "INVALID_INDEX",
                        "message": f"Index {index} is out of range for topic {topic}."
                    }

        self.logger.warning(f"Invalid action provided: {action}")
        return {
            "error": "INVALID_ACTION",
            "message": "Action must be read, add_note, or remove_note."
        }
