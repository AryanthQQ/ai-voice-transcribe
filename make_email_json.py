import json
import os

b_arr = ["gmail", "yahoo", "outlook", "hotmail", "protonmail", "mail", "email"]
fp_arr = ["notification", "login", "password", "app", "download", "spam", "inbox", "verification", "otp", "storage", "sync", "backup", "folder"]
i_arr = ["id", r"contact\s+me\s+on", r"pe\s+contact\s+karna", r"bhej\s+dena", r"address\s+share\s+karo", r"send\s+to", r"email\s+karo", r"mail\s+karo"]

data = {
  "base_keywords": b_arr,
  "intent_actions": i_arr,
  "false_positives": fp_arr
}

en_path = "backend/app/services/contact_detection/i18n/resources/en/email.json"
hi_path = "backend/app/services/contact_detection/i18n/resources/hi/email.json"

with open(en_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open(hi_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved EN and HI resources for Email")
