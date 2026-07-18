from .engine import ContactDetectionEngine
from .detectors.phone import PhoneDetector
from .detectors.whatsapp import WhatsAppDetector
from .detectors.instagram import InstagramDetector
from .detectors.telegram import TelegramDetector
from .detectors.email import EmailDetector
from .detectors.upi import UPIDetector
from .detectors.url import URLDetector

def get_engine() -> ContactDetectionEngine:
    engine = ContactDetectionEngine()
    engine.register_detector(PhoneDetector())
    # Registering empty detectors for future use
    engine.register_detector(WhatsAppDetector())
    engine.register_detector(InstagramDetector())
    engine.register_detector(TelegramDetector())
    engine.register_detector(EmailDetector())
    engine.register_detector(UPIDetector())
    engine.register_detector(URLDetector())
    return engine
