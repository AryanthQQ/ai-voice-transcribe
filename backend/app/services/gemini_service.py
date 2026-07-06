import json
from google import genai
from app.core.config import settings
from app.core.logger import logger

class GeminiService:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance

    def get_client(self):
        if self._client is None:
            try:
                self._client = genai.Client(vertexai=True, location=settings.VERTEX_LOCATION)
                logger.info("Gemini Vertex AI client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Vertex AI client: {e}")
                self._client = None
        return self._client

    def generate_text(self, prompt: str) -> str:
        client = self.get_client()
        if not client:
            raise ValueError("Gemini Client is not available.")
            
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")
            raise e

gemini_service = GeminiService()
