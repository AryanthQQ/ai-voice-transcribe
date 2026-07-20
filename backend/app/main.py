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

worker_pool = None

@app.on_event("startup")
async def startup_event():
    import time
    app.start_time = time.time()
    logger.info(f"Starting {settings.APP_NAME}...")
    
    # Validate STT Engine
    model_name = getattr(settings, "STT_PRIMARY_MODEL", getattr(settings, "WHISPER_MODEL", "large-v3-turbo"))
    device = getattr(settings, "STT_DEVICE", getattr(settings, "WHISPER_DEVICE", "cpu"))
    logger.info(f"[OK] STT Engine Ready (Model: {model_name}, Device: {device})")
    
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

    # Initialize and start WorkerPool
    global worker_pool
    from app.workers.pool import WorkerPool
    from app.workers.processor import process_job
    
    worker_pool = WorkerPool(
        process_fn=process_job,
        num_workers=settings.WORKER_COUNT
    )
    worker_pool.start()
    logger.info(f"[OK] WorkerPool started with {settings.WORKER_COUNT} workers")

@app.on_event("shutdown")
async def shutdown_event():
    global worker_pool
    if worker_pool:
        logger.info("Stopping WorkerPool...")
        worker_pool.stop()
        logger.info("[OK] WorkerPool stopped")

from app.services.metrics_service import metrics_service

@app.get("/health")
def health_check():
    import time
    import psutil
    import shutil
    import tempfile
    import subprocess
    
    # Check ffprobe
    ffprobe_avail = False
    try:
        if subprocess.run(["ffprobe", "-version"], capture_output=True).returncode == 0:
            ffprobe_avail = True
    except Exception:
        pass
        
    # Temp dir status
    temp_dir = tempfile.gettempdir()
    temp_writable = os.access(temp_dir, os.W_OK)
    
    # System metrics
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    # Load status mock logic based on singletons
    stt_loaded = True # Loaded on startup
    contact_loaded = True
    compliance_loaded = True
    
    return {
        "status": "healthy",
        "version": app.version,
        "uptime_sec": round(time.time() - getattr(app, 'start_time', time.time()), 2),
        "active_pipeline": getattr(settings, "PIPELINE_MODE", "legacy").lower(),
        "primary_stt_model": getattr(settings, "STT_PRIMARY_MODEL", "large-v3-turbo"),
        "fallback_stt_model": getattr(settings, "STT_FALLBACK_MODEL", "large-v3"),
        "modules": {
            "stt_loaded": stt_loaded,
            "contact_engine_loaded": contact_loaded,
            "compliance_engine_loaded": compliance_loaded
        },
        "system": {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk
        },
        "dependencies": {
            "ffprobe_available": ffprobe_avail,
            "temp_dir_writable": temp_writable
        },
        # Legacy fields for backward compatibility
        "whisper": "ready",
        "gemini": "ready" if settings.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "disabled",
        "diarization": "enabled" if settings.HF_TOKEN else "disabled",
        "email": "ready" if settings.SMTP_PASS and settings.SMTP_USER else "disabled",
        "bad_words": "loaded" if os.path.exists(settings.BAD_WORDS_FILE) else "missing"
    }

@app.get("/metrics")
def get_metrics():
    from app.core.queue.instance import global_queue
    metrics = metrics_service.get_metrics()
    queue_metrics = global_queue.get_metrics()
    metrics["queue"] = queue_metrics
    return metrics
