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

results = {}
for i, text in enumerate(test_cases, 1):
    results[f"test_{i}"] = detector.detect(text)

with open("instagram_baseline.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved baseline to instagram_baseline.json")
