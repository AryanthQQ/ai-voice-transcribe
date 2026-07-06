import os
import urllib.request
import torch
from pyannote.audio import Pipeline
from app.core.logger import logger

class DiarizeService:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DiarizeService, cls).__new__(cls)
        return cls._instance

    def load_pipeline(self):
        if self._pipeline is None:
            logger.info("Loading Pyannote Diarization pipeline into memory...")
            hf_token = os.environ.get("HF_TOKEN")
            if not hf_token:
                logger.error("HF_TOKEN missing. Diarization will not work.")
                raise ValueError("HF_TOKEN is required for Pyannote.")
            
            try:
                self._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1", 
                    use_auth_token=hf_token
                )
                if torch.cuda.is_available():
                    self._pipeline.to(torch.device("cuda"))
                logger.info("Pyannote pipeline loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Pyannote: {e}")
                raise e
        return self._pipeline

    def diarize(self, audio_path: str, num_speakers: int = 2):
        pipeline = self.load_pipeline()
        logger.info(f"Running diarization on {audio_path}")
        diarization = pipeline(audio_path, num_speakers=num_speakers)
        
        results = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            results.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        return results

diarize_service = DiarizeService()
