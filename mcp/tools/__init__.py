"""
Tools package for the AI Trust & Safety Engine MCP Server.

Each module in this package corresponds to one MCP tool.
All tools are read-only. No tool modifies any file or state.

Tool contract:
    - Every tool is a standalone Python function: handle() -> dict
    - Every tool returns the standard response envelope:
      {
        "tool": str,
        "source_file": str,
        "last_updated": str,
        "status": "current" | "outdated" | "draft",
        "data": dict,
        "warning": str | None
      }
    - Every tool is independently unit-testable without the MCP server.

Available tools:
    project_overview      -> get_project_overview()
    system_architecture   -> get_system_architecture()
    module_details        -> get_module_details(module_name: str)
    current_progress      -> get_current_progress()
    coding_standards      -> get_coding_standards()
    dependencies          -> get_dependencies(filter: str = None)
    known_issues          -> get_known_issues(severity: str = None)
    roadmap               -> get_roadmap(phase: str = None)
    file_structure        -> get_file_structure(path: str = None)
    search_knowledge      -> search_knowledge(query: str)
"""
