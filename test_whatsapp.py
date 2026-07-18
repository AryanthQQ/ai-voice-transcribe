import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection import get_engine

engine = get_engine()

# Test 1: Direct Keyword
print("Test 1 (Keyword):")
print(json.dumps(engine.analyze("Please send it on WA"), indent=2))

# Test 2: Intent Phrase
print("\nTest 2 (Intent):")
print(json.dumps(engine.analyze("sir apna WhatsApp number de do plz"), indent=2))

# Test 3: False Positive avoidance (swap, away)
print("\nTest 3 (False Positives):")
print(json.dumps(engine.analyze("I walked away and decided to swap my phone WP"), indent=2))

# Test 4: Hindi Devanagari
print("\nTest 4 (Hindi):")
print(json.dumps(engine.analyze("मुझे अपना वाट्सअप नंबर share karo"), indent=2))
