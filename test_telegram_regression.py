import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.detectors.telegram import TelegramDetector

detector = TelegramDetector()

test_cases = [
    "bhai apni telegram id de do",
    "join my group at t.me/trading_tips",
    "check this https://telegram.me/joinchat",
    "mujhe TG pe message karna",
    "I prefer Telegram over WhatsApp",
    "how to fix telegram app update",
    "telegram premium is good",
    "telegram notification sound"
]

with open("telegram_baseline.json", "r") as f:
    baseline = json.load(f)

for i, text in enumerate(test_cases, 1):
    result = detector.detect(text, language="hi")
    base_result = baseline[f"test_{i}"]
    if result != base_result:
        print(f"FAILED regression on test {i}: {text}")
        print("Expected:", json.dumps(base_result, indent=2))
        print("Got:", json.dumps(result, indent=2))
        sys.exit(1)

print("Telegram regression passed!")
