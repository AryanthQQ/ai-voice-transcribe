import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.detectors.instagram import InstagramDetector

detector = InstagramDetector()

test_cases = [
    "mera insta id hai anjali_123",
    "follow me on instagram @cool_guy",
    "mera @quantumquake",
    "insta pe aa jana yaar",
    "I use IG mostly",
    "how to download instagram reels",
    "instagram password reset",
    "follow me on instagram",
    "my insta ID is something"
]

with open("instagram_baseline.json", "r") as f:
    baseline = json.load(f)

for i, text in enumerate(test_cases, 1):
    result = detector.detect(text, language="hi")
    base_result = baseline[f"test_{i}"]
    if result != base_result:
        print(f"FAILED regression on test {i}: {text}")
        print("Expected:", json.dumps(base_result, indent=2))
        print("Got:", json.dumps(result, indent=2))
        sys.exit(1)

print("Instagram regression passed!")
