"""
Tool: build_context
MCP Tool Name: build_context

Purpose:
    Synthesize a complete, AI-ready context document by combining data from:
      1. ProjectScanner (live disk data)
      2. MemoryEngine (persistent state)
      3. KnowledgeBase (engineering standards)
      4. ProjectHealth (technical debt and diagnostics)

    Generates a structured engineering report with 10 sections:
      1. Project Overview
      2. Current Architecture
      3. Current Sprint
      4. Completed Features
      5. Pending Features
      6. Known Bugs
      7. Technical Debt
      8. Project Health
      9. Important Engineering Decisions
      10. Recommended Next Tasks
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from mcp.tools.base import BaseTool

class ContextBuilder(BaseTool):
    """
    Enterprise-grade Context Builder.
    Aggregates project context using injected tool dependencies.
    """

    def __init__(
        self,
        scanner: BaseTool,
        memory: BaseTool,
        kb: BaseTool,
        health: BaseTool,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.scanner = scanner
        self.memory = memory
        self.kb = kb
        self.health = health

    def _build_ai_summary(self, context: Dict[str, Any]) -> str:
        """
        Build the 10-section human-readable markdown report.
        """
        lines = ["# AI Trust & Safety Engine — Engineering Context\n"]
        
        # 1. Project Overview
        lines.append("## 1. Project Overview")
        if context.get("project_overview"):
            overview = context["project_overview"]
            lines.append(f"**Version:** {overview.get('version')}")
            if overview.get("goals"):
                lines.append("**Goals:**")
                for g in overview["goals"]:
                    lines.append(f"- {g}")
        
        # 2. Current Architecture
        lines.append("\n## 2. Current Architecture")
        arch = context.get("current_architecture", {})
        if isinstance(arch, dict):
            # Backward compatible dict format or new list format
            for layer in arch.get("layers", []):
                lines.append(f"- **{layer.get('name')}**: {layer.get('responsibility')}")
        elif isinstance(arch, list):
            for note in arch:
                lines.append(f"- {note}")
        else:
            lines.append("_No architecture details found._")

        # 3. Current Sprint
        lines.append("\n## 3. Current Sprint")
        sprint = context.get("current_sprint", [])
        if sprint:
            for item in sprint:
                lines.append(f"- {item}")
        else:
            lines.append("_No active sprint data._")

        # 4. Completed Features
        lines.append("\n## 4. Completed Features")
        completed = context.get("completed_features", [])
        if completed:
            for feat in completed:
                lines.append(f"- ✅ {feat}")
        else:
            lines.append("_No completed features logged._")

        # 5. Pending Features
        lines.append("\n## 5. Pending Features")
        pending = context.get("pending_features", [])
        if pending:
            for feat in pending:
                lines.append(f"- [ ] {feat}")
        else:
            lines.append("_No pending features logged._")

        # 6. Known Bugs
        lines.append("\n## 6. Known Bugs")
        bugs = context.get("known_bugs", [])
        if bugs:
            for bug in bugs:
                if isinstance(bug, dict):
                    lines.append(f"- 🐞 **{bug.get('id', 'BUG')} [{bug.get('severity', 'UNK')}]**: {bug.get('title', '')} - {bug.get('workaround', '')}")
                else:
                    lines.append(f"- 🐞 {bug}")
        else:
            lines.append("_No known bugs._")

        # 7. Technical Debt
        lines.append("\n## 7. Technical Debt")
        debt = context.get("technical_debt", {})
        if debt:
            if debt.get("broken_imports"):
                lines.append("**Broken Imports:**")
                for bi in debt["broken_imports"]:
                    lines.append(f"- {bi}")
            if debt.get("duplicate_logic"):
                lines.append("**Duplicate Logic:**")
                for dl in debt["duplicate_logic"]:
                    lines.append(f"- {dl}")
            if debt.get("missing_files"):
                lines.append("**Missing Files:**")
                for mf in debt["missing_files"]:
                    lines.append(f"- {mf}")
        else:
            lines.append("_No significant technical debt detected._")

        # 8. Project Health
        lines.append("\n## 8. Project Health")
        health_data = context.get("project_health", {})
        if health_data:
            lines.append(f"**Health Score:** {health_data.get('health_score', 'Unknown')}/100")
            stats = health_data.get("statistics", {})
            if stats:
                lines.append(f"**Files:** {stats.get('total_files', 0)} ({stats.get('total_size_mb', 0)} MB)")
                lines.append(f"**Python Files:** {stats.get('python_files', 0)}")
        else:
            lines.append("_Health data unavailable._")

        # 9. Important Engineering Decisions
        lines.append("\n## 9. Important Engineering Decisions")
        decisions = context.get("important_decisions", [])
        if decisions:
            for dec in decisions:
                lines.append(f"- {dec}")
        else:
            lines.append("_No engineering decisions logged._")

        # 10. Recommended Next Tasks
        lines.append("\n## 10. Recommended Next Tasks")
        next_tasks = context.get("recommended_next_tasks", [])
        if next_tasks:
            for task in next_tasks:
                lines.append(f"- ➡️ {task}")
        else:
            lines.append("_No tasks recommended._")

        return "\n".join(lines)

    def execute(
        self,
        include_file_tree: bool = True,
        include_python_details: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute ContextBuilder to synthesize the project context.
        """
        build_start = datetime.now(timezone.utc)
        self.logger.info("ContextBuilder starting synthesis")

        # 1. Fetch data from injected dependencies
        try:
            scanner_result = self.scanner.execute(project_root=kwargs.get("project_root"))
        except Exception as e:
            self.logger.error(f"ContextBuilder failed to execute scanner: {e}")
            scanner_result = {}

        try:
            memory_result = self.memory.execute("read")
            mem = memory_result.get("memory", {})
        except Exception as e:
            self.logger.error(f"ContextBuilder failed to read memory: {e}")
            mem = {}

        try:
            kb_result = self.kb.execute("read")
            kb_data = kb_result.get("data", {})
        except Exception as e:
            self.logger.error(f"ContextBuilder failed to read KB: {e}")
            kb_data = {}

        try:
            health_result = self.health.execute(project_root=kwargs.get("project_root"))
        except Exception as e:
            self.logger.error(f"ContextBuilder failed to execute project health: {e}")
            health_result = {}

        # 2. Map the 10 Requirements
        project_overview = {
            "version": mem.get("current_version", "unknown"),
            "goals": mem.get("project_goals", []),
            "summary": scanner_result.get("summary", {})
        }
        
        current_architecture = kb_data.get("architecture_notes", [])
        current_sprint = mem.get("next_sprint", [])
        completed_features = mem.get("completed_features", [])
        pending_features = mem.get("pending_features", [])
        known_bugs = mem.get("known_bugs", [])
        
        health_diagnostics = health_result.get("diagnostics", {})
        technical_debt = {
            "missing_files": health_diagnostics.get("missing_files", []),
            "broken_imports": health_diagnostics.get("broken_imports", []),
            "duplicate_logic": health_diagnostics.get("duplicate_logic", []),
            "potential_unused_files": health_diagnostics.get("potential_unused_files", [])
        }
        
        project_health = {
            "health_score": health_result.get("health_score", 0),
            "statistics": health_result.get("project_statistics", {})
        }
        
        important_decisions = mem.get("architecture_decisions", [])
        
        # Recommendations: pull from next_sprint if available, else pending features, else fix debt
        recommended_next_tasks = []
        if current_sprint:
            recommended_next_tasks = current_sprint[:3]
        elif pending_features:
            recommended_next_tasks = pending_features[:3]
        if technical_debt.get("broken_imports"):
            recommended_next_tasks.append("Fix broken imports to improve project health.")

        # 3. Assemble the new unified context payload
        context = {
            # New 10-section structured data
            "project_overview": project_overview,
            "current_architecture": current_architecture,
            "current_sprint": current_sprint,
            "completed_features": completed_features,
            "pending_features": pending_features,
            "known_bugs": known_bugs,
            "technical_debt": technical_debt,
            "project_health": project_health,
            "important_decisions": important_decisions,
            "recommended_next_tasks": recommended_next_tasks,
            
            # Legacy backward compatibility keys (mapped to new values where appropriate)
            "project_summary": project_overview,
            "features": {
                "implemented": completed_features,
                "in_progress": current_sprint,
                "pending": pending_features
            },
            "dependencies": scanner_result.get("requirements", {}),
            "current_todo": pending_features,
            "known_issues": known_bugs
        }

        # 4. Generate Markdown Report
        ai_ready_summary = self._build_ai_summary(context)

        build_duration_ms = int((datetime.now(timezone.utc) - build_start).total_seconds() * 1000)

        # 5. Construct final response matching previous API schema exactly
        response = {
            "tool": "build_context",
            "generated_at": build_start.isoformat(),
            "build_duration_ms": build_duration_ms,
            "context": context,
            "ai_ready_summary": ai_ready_summary,
            "api_surface": scanner_result.get("api_routes", []),
        }

        if include_file_tree:
            response["directory_tree"] = scanner_result.get("directory_tree", {})

        if include_python_details:
            response["python_files"] = scanner_result.get("python_files", [])

        self.logger.info(f"ContextBuilder finished in {build_duration_ms}ms")
        return response

# ---------------------------------------------------------------------------
# Backward Compatibility Shim
# ---------------------------------------------------------------------------
def handle(
    include_file_tree: bool = True,
    include_python_details: bool = False,
    **kwargs: Any
) -> dict:
    from mcp.config import AppConfig
    from mcp.utils.logger import get_logger
    from mcp.tools.project_scanner import ProjectScanner
    from mcp.tools.memory_engine import MemoryEngine
    from mcp.tools.knowledge_base import KnowledgeBase
    from mcp.tools.project_health import ProjectHealth
    
    config = AppConfig()
    logger = get_logger("context_builder")
    
    scanner = ProjectScanner(config, logger)
    memory = MemoryEngine(config, logger)
    kb = KnowledgeBase(config, logger)
    health = ProjectHealth(config, logger)
    
    tool = ContextBuilder(
        scanner=scanner,
        memory=memory,
        kb=kb,
        health=health,
        config=config,
        logger=logger
    )
    
    return tool.execute(
        include_file_tree=include_file_tree,
        include_python_details=include_python_details,
        **kwargs
    )

if __name__ == "__main__":
    result = handle(include_file_tree=False)
    print("=" * 70)
    print("CONTEXT BUILDER — AI-READY SUMMARY")
    print("=" * 70)
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(result.get("ai_ready_summary", ""))
