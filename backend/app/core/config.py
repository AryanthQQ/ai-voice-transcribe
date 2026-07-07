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
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: Optional[str] = None
    
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
    BAD_WORDS_FILE: str = str(BASE_DIR.parent / "bad_words.txt")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
