import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Enterprise AI Speech Analytics"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    PIPELINE_MODE: str = "legacy"  # modern or legacy
    
    # Worker & Queue Config
    QUEUE_TYPE: str = "memory"
    WORKER_COUNT: int = 5
    MAX_RETRIES: int = 3
    HEARTBEAT_TIMEOUT_SEC: int = 60
    
    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_ANALYSIS: str = "speech_analysis"
    KAFKA_CONSUMER_GROUP: str = "speech_analytics_group"
    
    # Audio Download Limits
    MAX_AUDIO_FILE_SIZE_MB: int = 50
    MAX_AUDIO_DURATION_SEC: int = 7200 # 2 hours
    
    # GCP / Gemini Config
    VERTEX_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    
    # Business Logic & Decision Config
    DECISION_RISK_THRESHOLD: int = 50
    DECISION_ACTION_MAPPING: dict = {
        "low": "ALLOW",
        "medium": "FLAG",
        "high": "BLOCK",
        "critical": "BLOCK"
    }
    
    # Email Trigger Config
    EMAIL_TRIGGER_VIOLATIONS: list = [
        "phone_number",
        "whatsapp",
        "telegram",
        "instagram",
        "email"
    ]
    
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_PROJECT: Optional[str] = None
    GCP_LOCATION: Optional[str] = None
    
    # Email Config
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    ALERT_EMAIL: str = ""
    
    # Legacy Whisper / Diarization Config (Backwards Compatibility)
    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    
    # Official STT Configuration
    STT_FRAMEWORK: str = "faster-whisper"
    STT_PRIMARY_MODEL: str = "large-v3-turbo"
    STT_FALLBACK_MODEL: str = "large-v3"
    STT_DEVICE: str = "cpu"
    STT_COMPUTE_TYPE: str = "int8"
    
    # Compliance Configuration
    COMPLIANCE_DETECTOR_WEIGHTS: Dict[str, int] = {
        "phone_number": 60,
        "whatsapp": 80,
        "instagram": 40,
        "telegram": 70,
        "email": 30,
        "upi": 90,
        "url": 50,
        "default": 10
    }
    
    HF_TOKEN: Optional[str] = None
    
    # Other APIs
    GROQ_API_KEY: Optional[str] = None
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    BAD_WORDS_FILE: str = str(BASE_DIR / "bad_words.txt")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Push GCP variables into the OS environment so the Google GenAI SDK can natively authenticate with the JSON file
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
if settings.GCP_PROJECT:
    os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GCP_PROJECT
if settings.GCP_LOCATION:
    os.environ["GOOGLE_CLOUD_LOCATION"] = settings.GCP_LOCATION
