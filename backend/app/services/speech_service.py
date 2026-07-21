import os
from faster_whisper import WhisperModel
from app.core.config import settings
from app.core.logger import logger

DEBUG_STT_CONFIG = True

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
            self.model_name = getattr(settings, "STT_PRIMARY_MODEL", getattr(settings, "WHISPER_MODEL", "large-v3-turbo"))
            self.device = getattr(settings, "STT_DEVICE", getattr(settings, "WHISPER_DEVICE", "cpu"))
            self.compute_type = getattr(settings, "STT_COMPUTE_TYPE", getattr(settings, "WHISPER_COMPUTE_TYPE", "int8"))
            
            logger.info(f"Loading Whisper model '{self.model_name}' into memory (Singleton)...")
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=4 if self.device == "cpu" else 0,
                num_workers=1
            )
            logger.info("Whisper model loaded successfully.")
        return self._model

    def transcribe(self, audio_path: str, language: str = None, prompt: str = None):
        model = self.load_model()
        
        logger.info(f"Transcribing audio file {audio_path}")
        
        if not prompt:
            prompt = "This audio contains conversational Hindi and Hinglish. Do not translate. Transcribe exactly as spoken. Phone numbers, WhatsApp numbers, UPI IDs and names should be written exactly as spoken. Do not invent English words."

        if DEBUG_STT_CONFIG:
            print("\n######## STT CONFIG ########")
            print(f"model name: {getattr(self, 'model_name', 'unknown')}")
            print(f"device: {getattr(self, 'device', 'unknown')}")
            print(f"compute_type: {getattr(self, 'compute_type', 'unknown')}")
            resolved_lang = language if language and language != "auto" else "auto"
            print(f"language: {resolved_lang}")
            print("beam_size: 5")
            print("vad_filter: True")
            print("vad_parameters: {'min_silence_duration_ms': 400}")
            print("condition_on_previous_text: False")
            print("temperature: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]")
            print(f"initial_prompt: {prompt}")
            print(f"audio path: {audio_path}")
            print("############################\n")
            
        # TEMPORARY STT EXPERIMENT
        # Used only to benchmark Hindi/Hinglish transcription accuracy.
        segments_gen, info = model.transcribe(
            audio_path,
            language="hi",
            initial_prompt=(
                "Primary language is Hindi. "
                "Keep English words exactly as spoken. "
                "Do not translate English words into Hindi. "
                "Write phone numbers using digits only. "
                "Preserve names exactly as spoken."
            ),
            beam_size=5,
            temperature=0,
            no_speech_threshold=0.6,
            condition_on_previous_text=True,
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 400
            }
        )
        
        logger.info(f"Detected language: {info.language}")
        logger.info(f"Probability: {info.language_probability}")
        logger.info(f"Duration: {info.duration} sec")
        logger.info(f"Model used: {getattr(self, 'model_name', 'unknown')}")
        
        segments = []
        for s in segments_gen:
            segments.append({
                "start": s.start,
                "end": s.end,
                "text": s.text.strip()
            })
            
        return segments, info

speech_service = SpeechService()
