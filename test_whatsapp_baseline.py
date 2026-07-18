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

results = {}
for i, text in enumerate(test_cases, 1):
    results[f"test_{i}"] = detector.detect(text)

with open("whatsapp_baseline.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved baseline to whatsapp_baseline.json")
