import os
from pathlib import Path

class AppConfig:
    """
    Central Configuration for the Enterprise MCP.
    Handles environment variables, paths, and dynamic thresholds.
    """
    
    def __init__(self):
        # Resolve the MCP directory (where this file lives)
        self.mcp_dir: Path = Path(__file__).resolve().parent
        
        # Resolve the Project Root (assuming mcp/ is at the root of the project)
        self.project_root: Path = self.mcp_dir.parent
        
        # Knowledge Base directory
        self.knowledge_dir: Path = self.mcp_dir / "knowledge"
        
        # Project health thresholds
        self.large_file_threshold_bytes: int = int(os.getenv("MCP_LARGE_FILE_THRESHOLD_BYTES", "50000"))
        
        # Logging settings
        self.log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO").upper()

    def get_knowledge_file_path(self, filename: str) -> Path:
        """Helper to safely construct paths to knowledge files."""
        return self.knowledge_dir / filename
