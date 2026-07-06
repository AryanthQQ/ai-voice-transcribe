import os
import tempfile
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from app.schemas.responses import AnalyzeCallResponse
from app.services.speech_service import speech_service
from app.core.logger import logger

router = APIRouter()

@router.post("/transcribe", response_model=AnalyzeCallResponse)
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form(None),
    prompt: str = Form(None),
    translate: str = Form("true")
):
    """
    Manual upload endpoint for transcribing an audio file directly from the UI.
    """
    temp_path = None
    try:
        original_name = file.filename or "audio.mp3"
        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else "mp3"
        allowed_exts = {"mp3", "wav", "webm", "m4a", "ogg", "flac", "mp4", "aac"}
        if ext not in allowed_exts:
            ext = "mp3"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
            temp_audio.write(await file.read())
            temp_path = temp_audio.name

        file_size_kb = os.path.getsize(temp_path) / 1024
        logger.info(f"Transcribing: {original_name} ({file_size_kb:.1f} KB), lang={language}, ext=.{ext}")
        
        if not prompt:
            prompt = "हाँ, ठीक है, जी, अच्छा।"

        segments, info = speech_service.transcribe(
            temp_path, 
            language=language, 
            prompt=prompt
        )
        
        turns = []
        full_text = ""
        
        # Simple non-diarized fallback for manual upload since we don't have pyannote here (matches old app.py)
        for seg in segments:
            text = seg["text"].strip()
            if text:
                full_text += text + " "
                mins = int(seg["start"] // 60)
                secs = int(seg["start"] % 60)
                turns.append({
                    "speaker": "SPEAKER_00",
                    "text": text,
                    "time": f"{mins}:{secs:02d}"
                })
                
        # To maintain compatibility with standard response
        return {
            "success": True,
            "transcript": full_text.strip(),
            "turns": turns,
            "language": info.language,
            "summary": None,
            "incidents": []
        }

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
