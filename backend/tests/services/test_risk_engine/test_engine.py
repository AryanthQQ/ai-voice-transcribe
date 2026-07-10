import pytest
from backend.app.services.intelligence.risk_engine.engine import RiskDecisionEngine
from backend.app.services.intelligence.risk_engine.models import RiskInput

@pytest.fixture
def engine():
    return RiskDecisionEngine()

def test_direct_contact_share(engine):
    # Mock inputs simulating both NumberEngine and ContactIntentEngine firing
    engines_data = {
        "NumberEngine": [
            {"entity_type": "PHONE_NUMBER", "confidence": 0.99, "normalized_value": "9876543210"}
        ],
        "ContactIntentEngine": [
            {"action": "MESSAGE", "channel": "WHATSAPP", "confidence": 0.95}
        ]
    }
    input_data = RiskInput(engines=engines_data)
    
    # Test default tenant
    result = engine.process(input_data, tenant_id="default")
    assert result.decision_rule == "DIRECT_CONTACT_SHARE"
    assert result.risk_level == "HIGH"
    assert result.recommended_action == "FLAG_FOR_REVIEW" # Default policy
    
    # Test dating_app tenant override
    result_dating = engine.process(input_data, tenant_id="dating_app")
    assert result_dating.recommended_action == "BLOCK"
    
    # Test bank tenant override
    result_bank = engine.process(input_data, tenant_id="bank")
    assert result_bank.recommended_action == "MASK_AND_LOG"
    
    # Verify evidence extraction
    assert len(result.evidence) == 2
    engines_triggered = [e.engine for e in result.evidence]
    assert "NumberEngine" in engines_triggered
    assert "ContactIntentEngine" in engines_triggered

def test_intent_only(engine):
    engines_data = {
        "NumberEngine": [],
        "ContactIntentEngine": [
            {"action": "MEET", "channel": "MEETING", "confidence": 0.9}
        ]
    }
    input_data = RiskInput(engines=engines_data)
    result = engine.process(input_data)
    
    assert result.decision_rule == "INTENT_ONLY"
    assert result.risk_level == "LOW"
    assert result.recommended_action == "ALLOW"
    
def test_no_risk(engine):
    engines_data = {
        "NumberEngine": [],
        "ContactIntentEngine": []
    }
    input_data = RiskInput(engines=engines_data)
    result = engine.process(input_data)
    
    assert result.decision_rule is None
    assert result.risk_level == "NONE"
    assert result.recommended_action == "ALLOW"
