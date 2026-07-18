import sys
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from backend.app.services.contact_detection.i18n.manager import i18n_manager
print("Resources EN:", i18n_manager.get_resource("phone", "number_words", "en"))
print("Resources phone_number:", i18n_manager.get_resource("phone_number", "number_words", "en"))
