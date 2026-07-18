import sys
import json
import re

base_keyword = r'\b(instagram|insta|ig)\b'
false_positives = r'(?!\s+(?:app|download|update|reels?|account\s+settings?|login|password))'
intent_actions = r'(?:id|follow(?:\s+me(?:\s+on)?)?|pe\s+aa\s+jana|pe\s+message\s+karna|share\s+karo|mera\s+(?:insta|instagram|ig)\s+hai|@[\w.]+)'

b_arr = ["instagram", "insta", "ig"]
fp_arr = ["app", "download", "update", r"reels?", r"account\s+settings?", "login", "password"]
i_arr = ["id", r"follow(?:\s+me(?:\s+on)?)?", r"pe\s+aa\s+jana", r"pe\s+message\s+karna", r"share\s+karo", r"mera\s+(?:insta|instagram|ig)\s+hai", r"@[\w.]+"]

data = {
  "base_keywords": b_arr,
  "intent_actions": i_arr,
  "false_positives": fp_arr
}

with open("backend/app/services/contact_detection/i18n/resources/en/instagram.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("backend/app/services/contact_detection/i18n/resources/hi/instagram.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved EN and HI resources")
