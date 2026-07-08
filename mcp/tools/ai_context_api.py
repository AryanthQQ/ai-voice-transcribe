"""
Tool: get_ai_context
MCP Tool Name: get_ai_context

Purpose:
    Provide a single machine-readable context endpoint that aggregates information
    from all underlying project tools.
    
    While `build_context` provides a human-readable engineering report, this tool
    provides the exact same intelligence in a strict, structured JSON format for
    AI systems to consume programmatically.
"""

import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from mcp.tools.base import BaseTool

class AIContextAPI(BaseTool):
    """
    Enterprise-grade AI Context API.
    Provides structured, machine-readable JSON context.
    """

    def __init__(
        self,
        scanner: BaseTool,
        memory: BaseTool,
        kb: BaseTool,
        health: BaseTool,
        context_builder: BaseTool,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.scanner = scanner
        self.memory = memory
        self.kb = kb
        self.health = health
        self.context_builder = context_builder

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the AI Context API to return structured JSON.
        """
        self.logger.info("AIContextAPI executing...")
        start_time = datetime.now(timezone.utc)
        
        # 1. Use the ContextBuilder to fetch all underlying aggregated data.
        # This prevents duplicating the logic of calling scanner, memory, kb, health.
        try:
            cb_result = self.context_builder.execute(**kwargs)
            ctx = cb_result.get("context", {})
        except Exception as e:
            self.logger.error(f"Failed to fetch data from ContextBuilder: {e}")
            ctx = {}

        # 2. Map to the strict schema required by the AI Context API
        structured_payload = {
            "project": ctx.get("project_overview", {}),
            "architecture": ctx.get("current_architecture", {}),
            "current_sprint": ctx.get("current_sprint", {}),
            "completed_features": ctx.get("completed_features", []),
            "pending_features": ctx.get("pending_features", []),
            "known_bugs": ctx.get("known_bugs", []),
            "technical_debt": ctx.get("technical_debt", {}),
            "health": ctx.get("project_health", {}),
            "engineering_decisions": ctx.get("important_decisions", []),
            "next_tasks": ctx.get("recommended_next_tasks", [])
        }
        
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        self.logger.info(f"AIContextAPI execution completed in {duration_ms}ms")

        # Backward Compatibility: Also execute underlying tools directly for legacy keys
        try:
            scanner_data = self.scanner.execute(**kwargs)
        except Exception:
            scanner_data = {}
            
        try:
            memory_data = self.memory.execute("read").get("memory", {})
        except Exception:
            memory_data = {}
            
        try:
            kb_data = self.kb.execute("read").get("data", {})
        except Exception:
            kb_data = {}

        # 3. Return the exact structure requested, wrapped in standard tool output envelope
        return {
            "tool": "get_ai_context",
            "generated_at": start_time.isoformat(),
            "timestamp": start_time.isoformat(),  # Legacy key
            "execution_duration_ms": duration_ms,
            "data": structured_payload,
            # Legacy keys for backward compatibility
            "project_disk_state": scanner_data,
            "project_memory_state": memory_data,
            "project_knowledge_base": kb_data
        }

# ---------------------------------------------------------------------------
# Backward Compatibility Shim
# ---------------------------------------------------------------------------
def handle(**kwargs: Any) -> dict:
    from mcp.config import AppConfig
    from mcp.utils.logger import get_logger
    from mcp.tools.project_scanner import ProjectScanner
    from mcp.tools.memory_engine import MemoryEngine
    from mcp.tools.knowledge_base import KnowledgeBase
    from mcp.tools.project_health import ProjectHealth
    from mcp.tools.context_builder import ContextBuilder
    
    config = AppConfig()
    logger = get_logger("ai_context_api")
    
    scanner = ProjectScanner(config, logger)
    memory = MemoryEngine(config, logger)
    kb = KnowledgeBase(config, logger)
    health = ProjectHealth(config, logger)
    context_builder = ContextBuilder(scanner, memory, kb, health, config=config, logger=logger)
    
    tool = AIContextAPI(
        scanner=scanner,
        memory=memory,
        kb=kb,
        health=health,
        context_builder=context_builder,
        config=config,
        logger=logger
    )
    
    return tool.execute(**kwargs)

if __name__ == "__main__":
    import json
    result = handle()
    print("=" * 70)
    print("AI CONTEXT API - STRUCTURED JSON RESPONSE")
    print("=" * 70)
    print(json.dumps(result["data"], indent=2))
