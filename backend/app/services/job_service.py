import uuid
from typing import Dict, Any

class JobManager:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._idempotency_map: Dict[str, str] = {}

    def create_job(self, request_id: str = None) -> str:
        if request_id and request_id in self._idempotency_map:
            return self._idempotency_map[request_id]

        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "RECEIVED",
            "progress": 0,
            "current_stage": "Received",
            "processing_time": "0.0 sec",
            "result": {}
        }
        
        if request_id:
            self._idempotency_map[request_id] = job_id
            
        return job_id

    def update_job(self, job_id: str, status: str, progress: int, current_stage: str, processing_time: str = "0.0 sec", result: dict = None, error: dict = None):
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = status
            self._jobs[job_id]["progress"] = progress
            self._jobs[job_id]["current_stage"] = current_stage
            self._jobs[job_id]["processing_time"] = processing_time
            if result is not None:
                self._jobs[job_id]["result"] = result
            if error is not None:
                self._jobs[job_id]["result"] = {"success": False, "error": error}

    def get_job(self, job_id: str) -> Dict[str, Any]:
        return self._jobs.get(job_id)

    def get_active_jobs_count(self) -> int:
        return sum(1 for j in self._jobs.values() if j["status"] not in ("COMPLETED", "FAILED", "DLQ"))

job_service = JobManager()
