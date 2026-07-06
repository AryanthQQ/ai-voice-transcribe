from fastapi import FastAPI
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

# Include routers
app.include_router(transcribe.router, prefix=settings.API_PREFIX, tags=["Transcription"])
app.include_router(analyze.router, prefix=settings.API_PREFIX, tags=["Analysis"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME}...")
    
@app.get("/")
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
