import sys
from pathlib import Path

# Add backend to path for tests
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from app.services.intelligence.number_engine import NumberEngine
from app.services.intelligence.number_engine.models.input import TranscriptSegment

def test_english_number():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="my phone number is nine double eight seven two three four five six zero",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "9887234560"
    assert res["entity_type"] == "PHONE_NUMBER"
    assert res["language"] == "en"

def test_hindi_number():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="mera number hai nau aath aath saat do teen chaar paanch chhe shunya",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "9887234560"
    assert res["entity_type"] == "PHONE_NUMBER"
    assert res["language"] == "hi"

def test_marathi_number():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="maza number nau aath aath saat don teen chaar paach saha shunya aahe",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "9887234560"
    assert res["entity_type"] == "PHONE_NUMBER"
    assert res["language"] == "mr"

def test_gujarati_number():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="maro number nav aath aath saat be tran chaar paanch chha shunya",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "9887234560"
    assert res["entity_type"] == "PHONE_NUMBER"
    assert res["language"] == "gu"

def test_otp_context():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="your otp is double four two one",
        start=0.0,
        end=2.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "4421"
    assert res["entity_type"] == "OTP"
    
def test_aadhaar_context():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="mera aadhaar number one two three four five six seven eight nine zero one two",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "123456789012"
    assert res["entity_type"] == "AADHAAR"

def test_invalid_length():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="phone number is nine double eight",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "988"
    assert res["validation_result"]["is_valid"] == False

def test_mixed_language():
    engine = NumberEngine()
    segment = TranscriptSegment(
        text="phone nine aath saat chha double two char panch six zero",
        start=0.0,
        end=5.0,
        speaker="SPEAKER_01",
        confidence=0.9
    )
    results = engine.extract_entities([segment.model_dump()])
    assert len(results) == 1
    res = results[0]
    assert res["normalized_value"] == "9876224560"
    assert res["entity_type"] == "PHONE_NUMBER"
    assert res["validation_result"]["is_valid"] == True

if __name__ == "__main__":
    print("Running Number Engine Tests...")
    test_english_number()
    test_hindi_number()
    test_marathi_number()
    test_gujarati_number()
    test_otp_context()
    test_aadhaar_context()
    test_invalid_length()
    test_mixed_language()
    print("All tests passed successfully!")

