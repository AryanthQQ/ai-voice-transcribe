import sys
import json
import re

b_arr = ["telegram", "tg"]
fp_arr = ["app", "download", "update", "login", "settings", "notification", "premium", r"channel\s+news"]
i_arr = ["id", "username", r"pe\s+aa\s+jana", r"pe\s+message\s+karna", r"share\s+karo", r"de\s+do"]
l_arr = [r"(?:https?://)?(?:t\.me|telegram\.me)/[\w.-]+"]

data = {
  "base_keywords": b_arr,
  "intent_actions": i_arr,
  "false_positives": fp_arr,
  "link_patterns": l_arr
}

with open("backend/app/services/contact_detection/i18n/resources/en/telegram.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("backend/app/services/contact_detection/i18n/resources/hi/telegram.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved EN and HI resources for Telegram")
