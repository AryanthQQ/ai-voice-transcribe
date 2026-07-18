import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection import get_engine
from backend.app.services.contact_detection.detectors.instagram import InstagramDetector

detector = InstagramDetector()

test_cases = [
    "mera insta id hai anjali_123", # Direct intent
    "follow me on instagram @cool_guy", # Follow request with @username context
    "mera @quantumquake", # Random handle (no context) -> should not trigger High
    "insta pe aa jana yaar", # Hinglish intent
    "I use IG mostly", # Standalone keyword -> Medium
    "how to download instagram reels", # False positive -> Ignored
    "instagram password reset", # False positive -> Ignored
    "follow me on instagram", # Just follow me on instagram -> High
    "my insta ID is something"
]

print("Running Instagram Detector Tests:")
for i, text in enumerate(test_cases, 1):
    result = detector.detect(text)
    print(f"\nTest {i}: {text}")
    print(json.dumps(result, indent=2))

