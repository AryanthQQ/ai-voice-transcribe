import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """Structured JSON formatter for Enterprise logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a structured JSON logger.
    
    Args:
        name: The name of the logger (typically __name__)
        level: The logging level
        
    Returns:
        A properly configured logging.Logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is fetched multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    logger.setLevel(level)
    return logger
