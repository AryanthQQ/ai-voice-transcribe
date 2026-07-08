"""
Tool: get_project_overview
MCP Name: get_project_overview
Knowledge Source: knowledge/project_overview.md

Returns: Mission, product philosophy, target users, current backend status,
         and why this is a Trust & Safety platform not a transcription tool.

IMPLEMENTATION STUB
-------------------
When implemented, this tool will:
1. Read knowledge/project_overview.md using frontmatter parser
2. Extract YAML header: domain, last_updated, updated_by, status
3. Parse sections: Mission, Product Philosophy, Target Users, Current Status
4. Return structured dict matching schemas/project_overview.schema.json
5. Attach warning if status == "outdated"
"""


def handle() -> dict:
    """
    Returns a structured summary of the project's mission, philosophy,
    and current deployment status.

    STUB — implement by reading knowledge/project_overview.md
    """
    raise NotImplementedError("Implement by reading knowledge/project_overview.md")
