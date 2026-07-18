import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.detectors.email import EmailDetector

detector = EmailDetector()

test_cases = [
    ("my address is user@example.com", "High"),
    ("Contact me on email", "High"),
    ("Gmail pe contact karna yaar", "High"),
    ("Email address share karo", "High"),
    ("I always use Gmail", "Ignored"),
    ("check the spam folder", "Ignored"),
    ("email password reset failed", "Ignored"),
    ("Gmail download", "Ignored")
]

failed = False
for text, expected in test_cases:
    res = detector.detect(text, language="hi")
    
    got_severity = "Ignored"
    if len(res) > 0:
        got_severity = res[0]["severity"].capitalize()
        
    if got_severity != expected:
        print(f"FAILED: '{text}' -> Expected {expected}, got {got_severity}")
        failed = True
    else:
        print(f"PASSED: '{text}' -> {expected}")

if failed:
    sys.exit(1)
print("All Email tests passed!")
