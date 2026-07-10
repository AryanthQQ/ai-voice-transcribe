from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid

class PipelineInput(BaseModel):
    """
    Input schema representing a processed transcript segment ready for analysis.
    """
    text: str
    start: float
    end: float
    speaker: str
    detected_language: str
    tenant_id: str = "default"
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class PipelineContext(BaseModel):
    """
    Shared execution context propagated through the pipeline to track state.
    """
    correlation_id: str
    input_data: PipelineInput
    execution_start_time: float
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)

class ExecutionMetrics(BaseModel):
    """
    Schema for execution performance metrics.
    """
    engine_metrics: Dict[str, float] = Field(default_factory=dict)
    total_latency_ms: float = 0.0

class PipelineResult(BaseModel):
    """
    Final integrated response from the intelligence pipeline.
    """
    correlation_id: str
    engines_output: Dict[str, List[Dict[str, Any]]]
    risk_assessment: Dict[str, Any]
    metrics: ExecutionMetrics
    failed_engines: List[str] = Field(default_factory=list)
