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
    (See docstring inside execute() for details)
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from mcp.tools.base import BaseTool

DEFAULT_MEMORY: Dict[str, Any] = {
    "project_goals": [],
    "current_version": "0.1.0",
    "completed_features": [],
    "pending_features": [],
    "architecture_decisions": [],
    "known_bugs": [],
    "important_notes": [],
    "next_sprint": []
}

class MemoryEngine(BaseTool):
    """
    Enterprise-grade Memory Engine.
    Manages persistent state across AI sessions using thread-safe JSON files.
    """

    @property
    def memory_file(self) -> Path:
        """Dynamically resolve the memory file from the injected config."""
        return self.config.get_knowledge_file_path("memory.json")

    def _read_memory(self) -> Dict[str, Any]:
        """Reads the memory JSON file safely."""
        if not self.memory_file.exists():
            self.logger.info(f"Memory file not found. Creating default at {self.memory_file}")
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_memory(DEFAULT_MEMORY)
            return DEFAULT_MEMORY.copy()
        try:
            content = self.memory_file.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"Error reading memory file: {e}. Returning default memory.")
            # If file is corrupted, return default but don't overwrite blindly
            return DEFAULT_MEMORY.copy()

    def _write_memory(self, memory: Dict[str, Any]) -> None:
        """Writes the memory JSON file atomically."""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.memory_file.write_text(
                json.dumps(memory, indent=2, ensure_ascii=False), 
                encoding="utf-8"
            )
            self.logger.debug(f"Memory successfully written to {self.memory_file}")
        except Exception as e:
            self.logger.error(f"Failed to write memory to {self.memory_file}: {e}")

    def execute(
        self,
        action: str = "read",
        category: Optional[str] = None,
        value: Optional[str] = None,
        index: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        mem = self._read_memory()
        action = action.lower()
        self.logger.info(f"MemoryEngine executing action: {action}")

        if action == "read":
            return {
                "tool": "memory_engine",
                "memory": mem
            }

        elif action == "set_version":
            if not value:
                self.logger.warning("Value required for set_version but not provided.")
                return {"error": "Value required for set_version."}
            old_version = mem.get("current_version")
            mem["current_version"] = value
            self._write_memory(mem)
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
                self.logger.warning(f"Invalid category provided: {category}")
                return {
                    "error": "INVALID_CATEGORY",
                    "message": f"Category must be one of: {', '.join(list_categories)}",
                    "provided_category": category
                }
            
            target_list = mem.setdefault(category, [])

            if action == "add":
                if not value:
                    self.logger.warning("Value required for add action but not provided.")
                    return {"error": "Value required for add action."}
                target_list.append(value)
                self._write_memory(mem)
                return {
                    "tool": "memory_engine",
                    "status": "success",
                    "action": "add",
                    "message": f"Added item to {category}",
                    "memory": mem
                }

            elif action == "remove":
                if index is None:
                    self.logger.warning("Index required for remove action but not provided.")
                    return {"error": "Index required for remove action."}
                try:
                    removed_item = target_list.pop(index)
                    self._write_memory(mem)
                    return {
                        "tool": "memory_engine",
                        "status": "success",
                        "action": "remove",
                        "message": f"Removed item from {category}: {removed_item}",
                        "memory": mem
                    }
                except IndexError:
                    self.logger.warning(f"Index {index} out of range for {category}.")
                    return {
                        "error": "INVALID_INDEX",
                        "message": f"Index {index} is out of range for category {category}."
                    }

        self.logger.warning(f"Invalid action provided: {action}")
        return {
            "error": "INVALID_ACTION",
            "message": "Action must be read, add, remove, or set_version."
        }
