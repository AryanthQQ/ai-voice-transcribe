import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.api.routes import transcribe, analyze

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise API for Speech Analytics",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.exceptions import RequestValidationError

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred processing the request.",
                "details": str(exc)
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters.",
                "details": exc.errors()
            }
        }
    )

# Include routers
app.include_router(transcribe.router, prefix=settings.API_PREFIX, tags=["Transcription"])
app.include_router(analyze.router, prefix=settings.API_PREFIX, tags=["Analysis"])

@app.on_event("startup")
async def startup_event():
    import time
    app.start_time = time.time()
    logger.info(f"Starting {settings.APP_NAME}...")
    
    # Validate Whisper
    logger.info(f"[OK] Whisper Ready (Model: {settings.WHISPER_MODEL}, Device: {settings.WHISPER_DEVICE})")
    
    # Validate Gemini
    if not settings.GOOGLE_APPLICATION_CREDENTIALS and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.warning("Gemini credentials missing. Analysis endpoints will return API errors.")
    else:
        logger.info("[OK] Gemini Ready")
        
    # Validate HF Token
    if not settings.HF_TOKEN:
        logger.warning("HF_TOKEN is missing. Diarization is disabled.")
    else:
        logger.info("[OK] Diarization Enabled (HF_TOKEN found)")
        
    # Validate SMTP
    if not settings.SMTP_PASS or not settings.SMTP_USER:
        logger.warning("SMTP credentials missing. Email alerts are disabled.")
    else:
        logger.info("[OK] Email Ready")
        
    # Validate Bad Words
    if os.path.exists(settings.BAD_WORDS_FILE):
        logger.info("[OK] Bad words list loaded")
    else:
        logger.warning(f"Bad words file not found at {settings.BAD_WORDS_FILE}")

from app.services.metrics_service import metrics_service

@app.get("/health")
def health_check():
    import time
    return {
        "status": "healthy",
        "whisper": "ready",
        "gemini": "ready" if settings.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "disabled",
        "diarization": "enabled" if settings.HF_TOKEN else "disabled",
        "email": "ready" if settings.SMTP_PASS and settings.SMTP_USER else "disabled",
        "bad_words": "loaded" if os.path.exists(settings.BAD_WORDS_FILE) else "missing",
        "uptime": f"{time.time() - getattr(app, 'start_time', time.time()):.2f} sec",
        "version": app.version
    }

@app.get("/metrics")
def get_metrics():
    return metrics_service.get_metrics()
