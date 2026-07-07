import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Enterprise AI Speech Analytics"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    
    # GCP / Gemini Config
    VERTEX_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_PROJECT: Optional[str] = None
    GCP_LOCATION: Optional[str] = None
    
    # Email Config
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    ALERT_EMAIL: str = ""
    
    # Whisper / Diarization Config
    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    HF_TOKEN: Optional[str] = None
    
    # Other APIs
    GROQ_API_KEY: Optional[str] = None
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    BAD_WORDS_FILE: str = str(BASE_DIR.parent / "public" / "bad_words.txt")

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
