import sys
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection import get_engine

engine = get_engine()

# Test 1: Transcript only (no segments) with standard number
violations = engine.analyze("call me at 9876543210 please")
print("Test 1 (Standard):", violations)

# Test 2: Segments with +91 and spaces
segments = [
    {"start": 12.5, "text": "my number is +91 9 8 7 6 5 4 3 2 1 0", "speaker": "Speaker 1"}
]
violations = engine.analyze("", segments)
print("Test 2 (Segments & Spaces):", violations)

# Test 3: Spoken English numbers
segments_spoken = [
    {"start": 65.0, "text": "you can dial nine eight seven six five four three two one zero", "speaker": "Speaker 2"}
]
violations_spoken = engine.analyze("", segments_spoken)
print("Test 3 (Spoken):", violations_spoken)

# Test 4: False positive check (should ignore a short price number)
violations_false = engine.analyze("that will cost 5000 rupees")
print("Test 4 (False Positive):", violations_false)
