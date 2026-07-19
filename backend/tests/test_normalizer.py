import pytest
from app.services.transcript_normalizer import transcript_normalizer

def test_whatsapp_normalization():
    assert transcript_normalizer.normalize("ये मेरा वाट्सब है") == "ये मेरा WhatsApp है"
    assert transcript_normalizer.normalize("Just ping me on what's up") == "Just ping me on WhatsApp"
    assert transcript_normalizer.normalize("व्हाट्सअप पर भेज दो") == "WhatsApp पर भेज दो"

def test_telegram_normalization():
    assert transcript_normalizer.normalize("टेली ग्राम डाउनलोड करो") == "Telegram डाउनलोड करो"

def test_email_normalization():
    assert transcript_normalizer.normalize("Send it on my मेल आईडी") == "Send it on my Email"
    assert transcript_normalizer.normalize("my Email ID is") == "my Email is"

def test_phone_number_normalization():
    assert transcript_normalizer.normalize("मेरा मोबाइल नंबर 9876543210 है") == "मेरा Phone Number 9876543210 है"
    assert transcript_normalizer.normalize("नंबर दे दो") == "Phone Number दे दो"

def test_digit_preservation_and_formatting():
    # Digits must never be lost, and spaces/dashes between them should be removed
    assert transcript_normalizer.normalize("9 8 7 6 5 4 3 2 1 0") == "9876543210"
    assert transcript_normalizer.normalize("98-76-54-32-10") == "9876543210"
    assert transcript_normalizer.normalize("98 765 43210") == "9876543210"
    
    # Should not remove spaces outside of digits
    assert transcript_normalizer.normalize("call 98 76 me") == "call 9876 me"

def test_noise_reduction():
    assert transcript_normalizer.normalize("hello   world") == "hello world"
    assert transcript_normalizer.normalize("wait,, what..") == "wait, what."
    assert transcript_normalizer.normalize("  too many   spaces  ") == "too many spaces"
