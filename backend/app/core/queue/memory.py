import time
import uuid
import threading
import heapq
from typing import Optional, Dict, Any
from .base import BaseQueue

class MemoryQueue(BaseQueue):
    def __init__(self, max_workers: int = 5, heartbeat_timeout: int = 60):
        self._max_workers = max_workers
        self._heartbeat_timeout = heartbeat_timeout
        self._lock = threading.RLock()
        
        # Priority queue implementation: list of tuples (-priority, enqueued_timestamp, job_id)
        self._queue = []
        
        # Job tracking
        self._jobs = {} # job_id -> payload
        self._idempotency_map = {} # request_id -> job_id
        
        # Active workers tracking: job_id -> { "worker_id": str, "last_heartbeat": float, "started_at": float, "payload": dict }
        self._active_jobs = {} 
        
        # Metrics
        self._metrics = {
            "completed_jobs": 0,
            "failed_jobs": 0,
            "dlq_jobs": 0,
            "total_wait_time": 0.0,
            "total_processing_time": 0.0
        }
        
    def enqueue(self, queue_name: str, payload: Dict[str, Any], priority: int = 0, request_id: str = None) -> str:
        with self._lock:
            if request_id and request_id in self._idempotency_map:
                return self._idempotency_map[request_id]
                
            job_id = str(uuid.uuid4())
            enqueued_at = time.time()
            
            job_entry = {
                "id": job_id,
                "queue_name": queue_name,
                "payload": payload,
                "priority": priority,
                "request_id": request_id,
                "enqueued_at": enqueued_at,
                "status": "QUEUED"
            }
            
            self._jobs[job_id] = job_entry
            if request_id:
                self._idempotency_map[request_id] = job_id
                
            # heapq is min-heap, so we negate priority for max-heap behavior
            heapq.heappush(self._queue, (-priority, enqueued_at, job_id))
            
            return job_id
            
    def dequeue(self, queue_name: str, worker_id: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        self._check_heartbeats()
        
        with self._lock:
            # We ignore queue_name in memory queue for simplicity, or we can filter
            temp_list = []
            job_id_to_return = None
            
            while self._queue:
                p, t, j_id = heapq.heappop(self._queue)
                job = self._jobs.get(j_id)
                
                if not job or job.get("queue_name") != queue_name or job.get("status") != "QUEUED":
                    continue
                    
                job_id_to_return = j_id
                break
                
            # Put back any non-matching items if we had to pop them (though we filtered during pop)
            if job_id_to_return:
                job = self._jobs[job_id_to_return]
                job["status"] = "RUNNING"
                
                now = time.time()
                wait_time = now - job["enqueued_at"]
                self._metrics["total_wait_time"] += wait_time
                
                self._active_jobs[job_id_to_return] = {
                    "worker_id": worker_id,
                    "last_heartbeat": now,
                    "started_at": now,
                    "job_id": job_id_to_return
                }
                
                return job
                
            return None
            
    def heartbeat(self, queue_name: str, job_id: str, worker_id: str) -> None:
        with self._lock:
            if job_id in self._active_jobs and self._active_jobs[job_id]["worker_id"] == worker_id:
                self._active_jobs[job_id]["last_heartbeat"] = time.time()

    def ack(self, queue_name: str, job_id: str) -> None:
        with self._lock:
            if job_id in self._active_jobs:
                active_job = self._active_jobs.pop(job_id)
                processing_time = time.time() - active_job["started_at"]
                self._metrics["total_processing_time"] += processing_time
                self._metrics["completed_jobs"] += 1
                
                if job_id in self._jobs:
                    self._jobs[job_id]["status"] = "COMPLETED"

    def nack(self, queue_name: str, job_id: str, requeue: bool = True) -> None:
        with self._lock:
            if job_id in self._active_jobs:
                active_job = self._active_jobs.pop(job_id)
                processing_time = time.time() - active_job["started_at"]
                self._metrics["total_processing_time"] += processing_time
                self._metrics["failed_jobs"] += 1
                
                if job_id in self._jobs:
                    job = self._jobs[job_id]
                    if requeue:
                        job["status"] = "QUEUED"
                        job["enqueued_at"] = time.time() # reset wait time
                        heapq.heappush(self._queue, (-job["priority"], job["enqueued_at"], job_id))
                    else:
                        job["status"] = "FAILED"

    def send_to_dlq(self, queue_name: str, payload: Dict[str, Any], error: str) -> None:
        with self._lock:
            job_id = payload.get("job_id")
            if job_id and job_id in self._active_jobs:
                self.nack(queue_name, job_id, requeue=False)
                
            if job_id and job_id in self._jobs:
                self._jobs[job_id]["status"] = "DLQ"
                self._jobs[job_id]["error"] = error
            
            self._metrics["dlq_jobs"] += 1

    def _check_heartbeats(self):
        with self._lock:
            now = time.time()
            orphaned = []
            for job_id, info in self._active_jobs.items():
                if now - info["last_heartbeat"] > self._heartbeat_timeout:
                    orphaned.append(job_id)
                    
            for job_id in orphaned:
                # Requeue orphaned jobs (could also depend on retry count)
                # We'll just NACK them and requeue
                if job_id in self._jobs:
                    queue_name = self._jobs[job_id].get("queue_name", "default")
                    self.nack(queue_name, job_id, requeue=True)
                    
    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            waiting = sum(1 for j in self._jobs.values() if j.get("status") == "QUEUED")
            running = len(self._active_jobs)
            completed = self._metrics["completed_jobs"]
            failed = self._metrics["failed_jobs"]
            
            total_handled = completed + failed
            avg_wait = self._metrics["total_wait_time"] / total_handled if total_handled > 0 else 0
            avg_proc = self._metrics["total_processing_time"] / total_handled if total_handled > 0 else 0
            
            utilization = (running / self._max_workers) * 100 if self._max_workers > 0 else 0
            
            return {
                "waiting_jobs": waiting,
                "running_jobs": running,
                "completed_jobs": completed,
                "failed_jobs": failed + self._metrics["dlq_jobs"],
                "dlq_jobs": self._metrics["dlq_jobs"],
                "avg_queue_wait_time_sec": round(avg_wait, 2),
                "avg_processing_time_sec": round(avg_proc, 2),
                "worker_utilization_percent": round(utilization, 2)
            }
