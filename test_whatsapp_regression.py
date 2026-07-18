import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.detectors.whatsapp import WhatsAppDetector

detector = WhatsAppDetector()

test_cases = [
    "WhatsApp number de do",
    "mera WA lelo",
    "Whats app share karo",
    "whatsapp update failed",
    "I use WP sometimes",
    "sirf whatsapp hi chalega",
]

with open("whatsapp_baseline.json", "r") as f:
    baseline = json.load(f)

for i, text in enumerate(test_cases, 1):
    result = detector.detect(text, language="hi")
    base_result = baseline[f"test_{i}"]
    if result != base_result:
        print(f"FAILED regression on test {i}: {text}")
        print("Expected:", json.dumps(base_result, indent=2))
        print("Got:", json.dumps(result, indent=2))
        sys.exit(1)

print("WhatsApp regression passed!")
