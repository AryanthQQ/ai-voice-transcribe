import abc
from dataclasses import dataclass
from typing import List, Tuple
import os

# We can reuse the backend's config to mirror production exactly.
import sys
from pathlib import Path
backend_path = str(Path(__file__).resolve().parents[2] / "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.core.config import settings

@dataclass
class STTSegment:
    start: float
    end: float
    text: str

class BaseSTT(abc.ABC):
    @abc.abstractmethod
    def load(self):
        """Load the model into memory."""
        pass

    @abc.abstractmethod
    def transcribe(self, audio_path: str) -> Tuple[str, List[STTSegment], str, float]:
        """
        Transcribe the audio file.
        Returns:
            Tuple containing:
            - full_transcript (str)
            - segments (List[STTSegment])
            - detected_language (str)
            - language_confidence (float)
        """
        pass

class FasterWhisperSTT(BaseSTT):
    def __init__(self, model_size: str):
        self.model_size = model_size
        self._model = None

    def load(self):
        from faster_whisper import WhisperModel
        
        # Load exactly as production does
        self._model = WhisperModel(
            self.model_size,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
            cpu_threads=4 if settings.WHISPER_DEVICE == "cpu" else 0,
            num_workers=1
        )

    def transcribe(self, audio_path: str) -> Tuple[str, List[STTSegment], str, float]:
        if not self._model:
            self.load()
            
        segments_gen, info = self._model.transcribe(
            audio_path,
            language=None,
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
        full_transcript = []
        
        for s in segments_gen:
            text = s.text.strip()
            full_transcript.append(text)
            segments.append(STTSegment(start=s.start, end=s.end, text=text))
            
        return " ".join(full_transcript), segments, info.language, info.language_probability

# Registry to effortlessly map CLI arguments to model adapters
MODEL_REGISTRY = {
    "large-v3": lambda: FasterWhisperSTT("large-v3"),
    "large-v3-turbo": lambda: FasterWhisperSTT("large-v3-turbo"),
    "distil-large-v3": lambda: FasterWhisperSTT("distil-large-v3"),
    "tiny": lambda: FasterWhisperSTT("tiny"),
    "base": lambda: FasterWhisperSTT("base"),
    "small": lambda: FasterWhisperSTT("small"),
    "medium": lambda: FasterWhisperSTT("medium")
}

def get_stt_model(model_name: str) -> BaseSTT:
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Model {model_name} not found in registry. Available: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[model_name]()
