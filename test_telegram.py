import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.detectors.telegram import TelegramDetector

detector = TelegramDetector()

test_cases = [
    "bhai apni telegram id de do", # Intent matched -> High
    "join my group at t.me/trading_tips", # Link matched -> High
    "check this https://telegram.me/joinchat", # Link matched -> High
    "mujhe TG pe message karna", # Intent matched -> High
    "I prefer Telegram over WhatsApp", # General discussion -> Ignored
    "how to fix telegram app update", # False positive -> Ignored
    "telegram premium is good", # False positive -> Ignored
    "telegram notification sound", # False positive -> Ignored
]

print("Running Telegram Detector Tests:")
for i, text in enumerate(test_cases, 1):
    result = detector.detect(text)
    print(f"\nTest {i}: {text}")
    print(json.dumps(result, indent=2))

