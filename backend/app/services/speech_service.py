import os
from faster_whisper import WhisperModel
from app.core.config import settings
from app.core.logger import logger

class SpeechService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechService, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        if self._model is None:
            logger.info(f"Loading Whisper model '{settings.WHISPER_MODEL}' into memory (Singleton)...")
            self._model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.WHISPER_DEVICE,
                compute_type=settings.WHISPER_COMPUTE_TYPE,
                cpu_threads=4 if settings.WHISPER_DEVICE == "cpu" else 0,
                num_workers=1
            )
            logger.info("Whisper model loaded successfully.")
        return self._model

    def transcribe(self, audio_path: str, language: str = None, prompt: str = None):
        model = self.load_model()
        
        logger.info(f"Transcribing audio file {audio_path}")
        segments_gen, info = model.transcribe(
            audio_path,
            language=language if language and language != "auto" else None,
            initial_prompt=prompt,
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            no_speech_threshold=0.6,
            vad_filter=False,
            beam_size=5,
        )
        
        segments = []
        for s in segments_gen:
            segments.append({
                "start": s.start,
                "end": s.end,
                "text": s.text.strip()
            })
            
        return segments, info

speech_service = SpeechService()
