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
            # Prefer STT_* config, fallback to legacy WHISPER_* if somehow missing or overriden incorrectly
            model_name = getattr(settings, "STT_PRIMARY_MODEL", getattr(settings, "WHISPER_MODEL", "large-v3-turbo"))
            device = getattr(settings, "STT_DEVICE", getattr(settings, "WHISPER_DEVICE", "cpu"))
            compute_type = getattr(settings, "STT_COMPUTE_TYPE", getattr(settings, "WHISPER_COMPUTE_TYPE", "int8"))
            
            logger.info(f"Loading Whisper model '{model_name}' into memory (Singleton)...")
            self._model = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type,
                cpu_threads=4 if device == "cpu" else 0,
                num_workers=1
            )
            logger.info("Whisper model loaded successfully.")
        return self._model

    def transcribe(self, audio_path: str, language: str = None, prompt: str = None):
        model = self.load_model()
        
        logger.info(f"Transcribing audio file {audio_path}")
        # TEMPORARY STT EXPERIMENT
        # Used only to benchmark Hindi/Hinglish transcription accuracy.
        segments_gen, info = model.transcribe(
            audio_path,
            language="hi",
            initial_prompt=prompt,
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            no_speech_threshold=0.6,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=400,
            ),
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
