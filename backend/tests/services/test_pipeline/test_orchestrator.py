import pytest
from backend.app.services.intelligence.pipeline.orchestrator import IntelligencePipeline
from backend.app.services.intelligence.pipeline.models import PipelineInput

@pytest.fixture
def pipeline():
    return IntelligencePipeline()

def test_successful_execution(pipeline):
    input_data = PipelineInput(
        text="hey message me on whatsapp my number is 9876543210",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_00",
        detected_language="en",
        tenant_id="dating_app"
    )
    
    result = pipeline.process(input_data)
    
    # 1. Verify general structure
    assert result.correlation_id is not None
    assert len(result.failed_engines) == 0
    assert result.metrics.total_latency_ms > 0
    
    # 2. Verify engines ran and populated data
    assert "NumberEngine" in result.engines_output
    assert "ContactIntentEngine" in result.engines_output
    
    number_results = result.engines_output["NumberEngine"]
    assert len(number_results) > 0
    assert number_results[0]["entity_type"] == "PHONE_NUMBER"
    
    intent_results = result.engines_output["ContactIntentEngine"]
    assert len(intent_results) > 0
    assert intent_results[0]["action"] == "MESSAGE"
    
    # 3. Verify risk engine triggered correctly based on policy
    # Dating app + Contact Share + Number Share -> BLOCK
    assert result.risk_assessment["recommended_action"] == "BLOCK"
    assert result.risk_assessment["risk_level"] == "HIGH"
    assert len(result.risk_assessment["evidence"]) == 2

def test_graceful_failure(pipeline):
    # Artificially inject a crash into NumberEngine
    def crashing_process(self, input_data):
        raise RuntimeError("Synthetic Crash")
    
    # Store original and override
    original_process = pipeline.number_engine.process_segment
    pipeline.number_engine.process_segment = crashing_process.__get__(pipeline.number_engine, type(pipeline.number_engine))
    
    try:
        input_data = PipelineInput(
            text="hey message me on whatsapp",
            start=0.0,
            end=2.0,
            speaker="SPEAKER_00",
            detected_language="en",
            tenant_id="default"
        )
        
        result = pipeline.process(input_data)
        
        # Should not crash entirely
        assert "NumberEngine" in result.failed_engines
        assert len(result.failed_engines) == 1
        
        # IntentEngine should still have run
        assert "ContactIntentEngine" in result.engines_output
        assert len(result.engines_output["ContactIntentEngine"]) > 0
        
        # RiskEngine should still have run and generated a decision (just without Number data)
        assert result.risk_assessment["recommended_action"] == "ALLOW"
        
    finally:
        # Restore
        pipeline.number_engine.process_segment = original_process
