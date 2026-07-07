import uuid
from typing import Dict, Any

class JobManager:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 5,
            "current_stage": "Queued",
            "processing_time": "0.0 sec",
            "result": {}
        }
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
                self._jobs[job_id]["result"] = {"success": False, "error": error} # Store error cleanly in result so API remains consistent

    def get_job(self, job_id: str) -> Dict[str, Any]:
        return self._jobs.get(job_id)

    def get_active_jobs_count(self) -> int:
        return sum(1 for j in self._jobs.values() if j["status"] not in ("completed", "failed"))

job_service = JobManager()
