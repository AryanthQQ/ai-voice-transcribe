"""
Tool: get_current_progress
MCP Name: get_current_progress
Knowledge Source: knowledge/progress.md

Returns: A structured breakdown of:
    - COMPLETED modules and features (with completion date)
    - IN_PROGRESS work (with owner and target date)
    - PENDING work (prioritized backlog)
    - Blocking issues

This is the first tool any AI should call when joining an engineering session.
It answers: "Where are we right now?"

IMPLEMENTATION STUB
-------------------
When implemented, this tool will:
1. Read knowledge/progress.md
2. Parse sections: Completed, In Progress, Pending, Blockers
3. Return structured dict matching schemas/progress.schema.json
4. Surface a staleness warning if last_updated > 7 days ago
"""


def handle() -> dict:
    """
    Returns the current project progress: completed, in-progress, pending.

    STUB — implement by reading knowledge/progress.md
    """
    raise NotImplementedError("Implement by reading knowledge/progress.md")
