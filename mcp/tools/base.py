from abc import ABC, abstractmethod
from typing import Any, Dict
import logging
from mcp.config import AppConfig

class BaseTool(ABC):
    """
    Abstract Base Class for all Enterprise MCP Tools.
    Enforces Dependency Injection and a standard execution interface.
    """
    
    def __init__(self, config: AppConfig, logger: logging.Logger):
        """
        Inject core dependencies.
        
        Args:
            config: The central application configuration
            logger: The structured logger for the module
        """
        self.config = config
        self.logger = logger
        
    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        The primary execution entry point for the tool.
        Must return a dictionary that acts as the JSON response payload.
        
        Args:
            **kwargs: Dynamic arguments matching the FastMCP tool signature
            
        Returns:
            Dict: The structured response payload
        """
        pass
