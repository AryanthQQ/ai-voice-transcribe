import sys
import json
from pathlib import Path
sys.path.append(str(Path('backend').resolve()))

from app.services.compliance.engine import ComplianceEngine

engine = ComplianceEngine()

raw_violations = [
    {
        "type": "phone_number",
        "severity": "High",
        "confidence": 0.8,
        "matched_text": "9876543210",
        "value": "9876543210"
    },
    {
        # Duplicate phone
        "type": "phone_number",
        "severity": "High",
        "confidence": 0.99,
        "matched_text": "9876543210",
        "value": "9876543210"
    },
    {
        "type": "whatsapp",
        "severity": "Medium",
        "confidence": 0.70,
        "matched_text": "WA"
    }
]

# phone_number (60) + whatsapp (80) = 140 -> Capped at 100 -> Critical
report = engine.process_violations("CALL_TEST_123", raw_violations)
print(json.dumps(report, indent=2))
