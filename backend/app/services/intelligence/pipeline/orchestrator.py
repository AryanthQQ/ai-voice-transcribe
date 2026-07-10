import time
import traceback
from typing import Dict, Any

from .models import PipelineInput, PipelineContext, ExecutionMetrics, PipelineResult
from .registry import EngineRegistry
from . import events

# Upstream Engines
from app.services.intelligence.number_engine.engine import NumberEngine
from app.services.intelligence.number_engine.models.input import TranscriptSegment
from app.services.intelligence.contact_intent_engine.engine import ContactIntentEngine
from app.services.intelligence.contact_intent_engine.models import IntentInput
from app.services.intelligence.risk_engine.engine import RiskDecisionEngine
from app.services.intelligence.risk_engine.models import RiskInput

class IntelligencePipeline:
    """
    Central orchestration layer. Contains no business logic.
    """
    def __init__(self):
        self.registry = EngineRegistry()
        
        # Initialize standard engines
        self.number_engine = NumberEngine()
        self.intent_engine = ContactIntentEngine()
        self.risk_engine = RiskDecisionEngine()
        
        # Register engines with their context adapter functions
        self.registry.register("NumberEngine", self.number_engine, self._adapter_number)
        self.registry.register("ContactIntentEngine", self.intent_engine, self._adapter_intent)
        # RiskEngine is handled separately at the end as it consumes all outputs

    def _adapter_number(self, context: PipelineContext) -> TranscriptSegment:
        return TranscriptSegment(
            text=context.input_data.text,
            start=context.input_data.start,
            end=context.input_data.end,
            speaker=context.input_data.speaker,
            confidence=1.0,
            detected_language=context.input_data.detected_language
        )

    def _adapter_intent(self, context: PipelineContext) -> IntentInput:
        return IntentInput(
            text=context.input_data.text,
            start=context.input_data.start,
            end=context.input_data.end,
            speaker=context.input_data.speaker,
            confidence=1.0,
            detected_language=context.input_data.detected_language
        )

    def process(self, input_data: PipelineInput) -> PipelineResult:
        start_time = time.time()
        context = PipelineContext(
            correlation_id=input_data.correlation_id,
            input_data=input_data,
            execution_start_time=start_time
        )
        
        metrics = ExecutionMetrics()
        failed_engines = []
        
        execution_plan = self.registry.get_execution_plan()
        
        # 1. Execute Intelligence Engines
        for plan in execution_plan:
            name = plan["name"]
            instance = plan["instance"]
            adapter = plan["adapter"]
            
            events.emit_engine_started(context.correlation_id, name)
            engine_start = time.time()
            
            try:
                # Map context to engine specific input
                engine_input = adapter(context)
                
                # Execute engine
                if hasattr(instance, "process_segment"):
                    result = instance.process_segment(engine_input)
                else:
                    result = instance.process(engine_input)
                
                # Convert results to dict for standardized serialization
                serialized_result = [r.model_dump() if hasattr(r, "model_dump") else r for r in result]
                context.intermediate_results[name] = serialized_result
                
                engine_latency = (time.time() - engine_start) * 1000
                metrics.engine_metrics[name] = engine_latency
                events.emit_engine_completed(context.correlation_id, name, engine_latency)
                
            except Exception as e:
                error_msg = str(e)
                failed_engines.append(name)
                events.emit_engine_failed(context.correlation_id, name, error_msg)
                
        # 2. Execute Risk Decision Engine
        events.emit_engine_started(context.correlation_id, "RiskDecisionEngine")
        risk_start = time.time()
        try:
            risk_input = RiskInput(engines=context.intermediate_results)
            risk_result = self.risk_engine.process(risk_input, tenant_id=input_data.tenant_id)
            
            risk_latency = (time.time() - risk_start) * 1000
            metrics.engine_metrics["RiskDecisionEngine"] = risk_latency
            events.emit_engine_completed(context.correlation_id, "RiskDecisionEngine", risk_latency)
            events.emit_decision_completed(context.correlation_id, risk_result.risk_level, risk_result.recommended_action)
            
        except Exception as e:
            error_msg = str(e)
            failed_engines.append("RiskDecisionEngine")
            events.emit_engine_failed(context.correlation_id, "RiskDecisionEngine", error_msg)
            # Fallback risk result
            from backend.app.services.intelligence.risk_engine.models import RiskResult
            risk_result = RiskResult()

        metrics.total_latency_ms = (time.time() - start_time) * 1000
        
        # Ensure risk_result is dumped properly
        risk_assessment_dict = risk_result.model_dump() if hasattr(risk_result, "model_dump") else {}

        return PipelineResult(
            correlation_id=context.correlation_id,
            engines_output=context.intermediate_results,
            risk_assessment=risk_assessment_dict,
            metrics=metrics,
            failed_engines=failed_engines
        )
