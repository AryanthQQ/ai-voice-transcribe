import pytest
import os
from backend.app.services.intelligence.contact_intent_engine.engine import ContactIntentEngine
from backend.app.services.intelligence.contact_intent_engine.models import IntentInput

@pytest.fixture
def engine():
    return ContactIntentEngine()

def test_simple_whatsapp(engine):
    input_data = IntentInput(
        text="hey message me on whatsapp",
        start=0.0,
        end=1.5,
        speaker="SPEAKER_00",
        confidence=0.9,
        detected_language="en"
    )
    results = engine.process(input_data)
    
    assert len(results) == 1
    assert results[0].intent == "CONTACT_SHARE"
    assert results[0].channel == "WHATSAPP"
    assert results[0].action == "MESSAGE"

def test_hindi_intent(engine):
    input_data = IntentInput(
        text="bhai mujhe mera number whatsapp karo",
        start=1.0,
        end=2.5,
        speaker="SPEAKER_01",
        confidence=0.8
    )
    results = engine.process(input_data)
    
    assert len(results) == 1
    assert results[0].channel == "WHATSAPP"
    assert results[0].action == "MESSAGE"

def test_false_positive_rejection(engine):
    input_data = IntentInput(
        text="you can download whatsapp from the app store",
        start=0.0,
        end=2.0,
        speaker="SPEAKER_00",
        confidence=0.9
    )
    results = engine.process(input_data)
    
    # Should not trigger contact share due to "download whatsapp"
    assert len(results) == 0

def test_multiple_intents(engine):
    input_data = IntentInput(
        text="either whatsapp me or call me",
        start=0.0,
        end=2.0,
        speaker="SPEAKER_00",
        confidence=0.9
    )
    results = engine.process(input_data)
    
    assert len(results) == 2
    channels = [r.channel for r in results]
    assert "WHATSAPP" in channels
    assert "CALL" in channels
