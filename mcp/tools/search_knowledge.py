"""
Tool: search_knowledge
MCP Name: search_knowledge
Knowledge Source: ALL knowledge/**/*.md files

Parameters:
    query (str): Free-text search query. Example: "OTP detection", "Pyannote", "risk score"

Returns: Ranked list of matching excerpts from the knowledge base, with
         file paths and relevance scores. Top 5 results maximum.

This tool is the fallback for any AI that doesn't know which specific tool to call.

Search Strategy:
    Token-based TF-IDF over all .md files in knowledge/.
    No semantic embeddings. No external API calls.
    Purely local, deterministic, reproducible.

IMPLEMENTATION STUB
-------------------
When implemented, this tool will:
1. Walk all .md files under knowledge/
2. Build an in-memory inverted index (lazy, cached after first call)
3. Score documents against query tokens using TF-IDF
4. Return top-5 results with file path, matched excerpt, and relevance score
5. Return empty results with a suggestion if no match found
"""


def handle(query: str) -> dict:
    """
    Full-text search across the entire MCP knowledge base.

    STUB — implement TF-IDF search over knowledge/**/*.md
    """
    raise NotImplementedError(
        "Implement TF-IDF search over all files in knowledge/**/*.md"
    )
