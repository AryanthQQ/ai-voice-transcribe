import sys
import json
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.base import BaseContactDetector

print("Base module contents:")
with open("backend/app/services/contact_detection/base.py", "r") as f:
    print(f.read())
