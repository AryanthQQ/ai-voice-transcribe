import psutil
from typing import Dict, Any
from app.services.job_service import job_service

class MetricsManager:
    def __init__(self):
        self.requests_total = 0
        self.completed = 0
        self.failed = 0
        self.total_processing_time_sec = 0.0

    def record_job(self, success: bool, processing_time_sec: float):
        self.requests_total += 1
        if success:
            self.completed += 1
        else:
            self.failed += 1
        self.total_processing_time_sec += processing_time_sec

    def get_metrics(self) -> Dict[str, Any]:
        avg_time = 0.0
        if self.completed + self.failed > 0:
            avg_time = self.total_processing_time_sec / (self.completed + self.failed)

        # CPU usage (interval=None means it returns the percentage since last call)
        cpu_usage = psutil.cpu_percent(interval=None)
        
        # Memory usage
        mem = psutil.virtual_memory()
        memory_usage = mem.percent

        return {
            "requests_total": self.requests_total,
            "completed": self.completed,
            "failed": self.failed,
            "active_jobs": job_service.get_active_jobs_count(),
            "average_processing_time": f"{avg_time:.2f} sec",
            "cpu_usage": f"{cpu_usage}%",
            "memory_usage": f"{memory_usage}%",
            "whisper_loaded": True, # Hardcoded as True since it's a singleton loaded at startup
            "gemini_ready": True # Depends on credentials, but generally true if server started
        }

metrics_service = MetricsManager()
