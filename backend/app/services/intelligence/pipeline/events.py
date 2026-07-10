import logging
from typing import Any, Dict

# Basic logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PipelineEvents")

def _log_event(event_name: str, correlation_id: str, engine_name: str, details: Dict[str, Any] = None):
    """
    Format and emit a structured event log.
    """
    base_log = f"[{correlation_id}] {event_name} | Engine={engine_name}"
    if details:
        base_log += f" | Details={details}"
    logger.info(base_log)

def emit_engine_started(correlation_id: str, engine_name: str):
    _log_event("EngineStarted", correlation_id, engine_name)

def emit_engine_completed(correlation_id: str, engine_name: str, latency_ms: float):
    _log_event("EngineCompleted", correlation_id, engine_name, {"latency_ms": f"{latency_ms:.2f}"})

def emit_engine_failed(correlation_id: str, engine_name: str, error_message: str):
    _log_event("EngineFailed", correlation_id, engine_name, {"error": error_message})
    logger.error(f"[{correlation_id}] {engine_name} encountered an exception: {error_message}")

def emit_decision_completed(correlation_id: str, risk_level: str, action: str):
    _log_event("DecisionCompleted", correlation_id, "RiskDecisionEngine", {"risk_level": risk_level, "action": action})
