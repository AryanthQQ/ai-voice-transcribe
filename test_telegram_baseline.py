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

results = {}
for i, text in enumerate(test_cases, 1):
    results[f"test_{i}"] = detector.detect(text)

with open("telegram_baseline.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved baseline to telegram_baseline.json")
