import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.detectors.phone import PhoneDetector

detector = PhoneDetector()

print("--- Testing English ---")
en_res = detector.detect("my number is nine eight seven six five four three two one zero", language="en")
print(json.dumps(en_res, indent=2))

print("\n--- Testing Hindi ---")
hi_res = detector.detect("mera number nau aath saat chhe paanch char teen do ek shunya hai", language="hi")
print(json.dumps(hi_res, indent=2))

print("\n--- Testing Unknown Language (Fallback to English) ---")
unk_res = detector.detect("call me at nine eight seven six five four three two one zero")
print(json.dumps(unk_res, indent=2))

print("\n--- Testing Hybrid ---")
hybrid_res = detector.detect("call nine eight seven 6 5 4 teen 2 ek zero", language="hi")
print(json.dumps(hybrid_res, indent=2))
