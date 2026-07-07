from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from app.schemas.requests import AnalyzeCallRequest
from app.schemas.responses import AnalyzeCallResponse
from app.services.worker_service import process_call_audio
from app.core.logger import logger

router = APIRouter()

@router.post("/analyze-call", response_model=AnalyzeCallResponse)
async def analyze_call(
    user_id: str = Form(None),
    sender_ref_code: str = Form(None),
    adviser_id: str = Form(None),
    reciever_ref_code: str = Form(None),
    voice_url: str = Form(...)
):
    """
    Webhook endpoint for n8n to analyze a recorded call.
    Accepts both standard and alternate n8n parameter names.
    """
    final_user_id = sender_ref_code or user_id
    final_adviser_id = reciever_ref_code or adviser_id
    
    if not voice_url:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error": {
                "code": "MISSING_PARAMETER",
                "message": "voice_url is required",
                "details": "The voice_url parameter must be provided."
            }
        })
        
    logger.info(f"Received webhook: adviser={final_adviser_id}, user={final_user_id}, url={voice_url}")
    
    result = process_call_audio(final_adviser_id, final_user_id, voice_url)
    
    if not result.get("success"):
        logger.error(f"Analysis failed: {result.get('error')}")
        return JSONResponse(status_code=500, content=result)
        
    return result
