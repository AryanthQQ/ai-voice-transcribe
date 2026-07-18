from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from app.services.job_service import job_service
from app.core.queue.instance import global_queue
from app.core.logger import logger

router = APIRouter()

@router.post("/analyze-call")
async def analyze_call(
    user_id: str = Form(None),
    sender_ref_code: str = Form(None),
    adviser_id: str = Form(None),
    reciever_ref_code: str = Form(None),
    voice_url: str = Form(...),
    request_id: str = Form(None),
    priority: int = Form(0)
):
    """
    Webhook endpoint for n8n to asynchronously analyze a recorded call.
    Accepts both standard and alternate n8n parameter names.
    Returns a job_id immediately.
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
        
    logger.info(f"Received webhook: adviser={final_adviser_id}, user={final_user_id}, url={voice_url}, req_id={request_id}")
    
    # Use the job_service for idempotent job creation (registers the job with the service)
    job_id = job_service.create_job(request_id=request_id)
    
    # We update to queued state
    job_service.update_job(job_id, "QUEUED", 5, "Queued in Message Broker")
    
    payload = {
        "job_id": job_id,
        "adviser_id": final_adviser_id,
        "user_id": final_user_id,
        "voice_url": voice_url,
        "retries": 0
    }
    
    # Enqueue using the global queue interface
    # (If the queue handles idempotency it will return the same job_id, 
    # but job_service already handles the idempotency mapping for the API boundary).
    global_queue.enqueue(
        queue_name="analysis_jobs",
        payload=payload,
        priority=priority,
        request_id=request_id
    )
    
    return JSONResponse(status_code=202, content={"job_id": job_id})

@router.get("/analyze-status/{job_id}")
async def get_analyze_status(job_id: str):
    """
    Check the status of an ongoing analysis job.
    When complete, this will contain the final result payload.
    """
    job = job_service.get_job(job_id)
    if not job:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": {
                "code": "JOB_NOT_FOUND",
                "message": f"No job found with ID {job_id}"
            }
        })
        
    return JSONResponse(status_code=200, content=job)
