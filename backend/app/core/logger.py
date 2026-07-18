import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate logs if logger is already configured
    if logger.handlers:
        return logger
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Standard enterprise log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

logger = setup_logger("ai-speech-analytics")

import json
from typing import Any, Dict

def log_structured(event_name: str, data: Dict[str, Any], level: int = logging.INFO):
    """
    Emits a structured JSON log entry for observability platforms.
    """
    payload = {
        "event": event_name,
        **data
    }
    logger.log(level, json.dumps(payload))
