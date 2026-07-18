import sys
import json
import re

base = r'\b(?:whatsapp|whats\s*app|wa|wp|  _ Y? , . | 慝? 1 _ Y? , ? | 慝? 1 _ Y? , ? ? )\b'
actions = r'(?:number|message|share|aa\s*jana|de\s*do|mil\s*sakta\s*hai|karna|do)'

# Strip wrappers to get array
b_arr = base.replace(r'\b(?:', '').replace(r')\b', '').split('|')
a_arr = actions.replace(r'(?:', '').replace(r')', '').split('|')

data = {
  "base_keywords": b_arr,
  "intent_actions": a_arr
}

with open("backend/app/services/contact_detection/i18n/resources/hi/whatsapp.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved HI resources")
