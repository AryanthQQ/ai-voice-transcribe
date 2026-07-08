"""
Future Modules Stubs
MCP Tool Name: Various

Purpose:
    Provides the architectural placeholders for Phase 2/3 Enterprise MCP features.
    These tools are currently stubs returning 'NOT_IMPLEMENTED', ensuring that
    any AI analyzing the server understands the planned future capabilities and
    the boundaries of the current architecture.

Supported Future Modules:
    - Git Integration
    - Issue Tracking
    - PR Review
    - Architecture Review
    - Automatic Documentation
    - Code Review
    - Test Summary
    - Dependency Graph
"""

def _stub_response(module_name: str, expected_input: str) -> dict:
    return {
        "tool": module_name,
        "status": "NOT_IMPLEMENTED",
        "message": f"The {module_name} module is planned for a future architecture phase.",
        "expected_input": expected_input
    }

def handle_git_integration() -> dict:
    return _stub_response("git_integration", "git command or operation")

def handle_issue_tracking() -> dict:
    return _stub_response("issue_tracking", "issue ID or Jira/Linear payload")

def handle_pr_review() -> dict:
    return _stub_response("pr_review", "PR number or branch name")

def handle_architecture_review() -> dict:
    return _stub_response("architecture_review", "Diff or structural change description")

def handle_automatic_documentation() -> dict:
    return _stub_response("automatic_documentation", "Module path to document")

def handle_code_review() -> dict:
    return _stub_response("code_review", "File path or git diff")

def handle_test_summary() -> dict:
    return _stub_response("test_summary", "Test runner output or JUnit XML")

def handle_dependency_graph() -> dict:
    return _stub_response("dependency_graph", "Package manager (pip/npm) context")
