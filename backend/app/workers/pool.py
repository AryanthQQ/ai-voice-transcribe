import threading
import time
import uuid
from typing import Callable, Any
from app.core.queue.instance import global_queue
from app.core.logger import logger
from app.core.config import settings

class WorkerPool:
    def __init__(self, process_fn: Callable[[dict], None], num_workers: int = settings.WORKER_COUNT):
        self.process_fn = process_fn
        self.num_workers = num_workers
        self.workers = []
        self._stop_event = threading.Event()
        
    def start(self):
        logger.info(f"Starting worker pool with {self.num_workers} workers...")
        for i in range(self.num_workers):
            worker_id = f"worker-{i}-{uuid.uuid4().hex[:6]}"
            t = threading.Thread(target=self._worker_loop, args=(worker_id,), daemon=True)
            t.start()
            self.workers.append(t)
            
    def stop(self):
        logger.info("Stopping worker pool...")
        self._stop_event.set()
        for t in self.workers:
            t.join(timeout=2)
            
    def _worker_loop(self, worker_id: str):
        logger.info(f"[{worker_id}] Started.")
        while not self._stop_event.is_set():
            try:
                # Dequeue a job (waits for timeout)
                job = global_queue.dequeue(queue_name="analysis_jobs", worker_id=worker_id, timeout=2)
                
                if job:
                    job_id = job["id"]
                    payload = job["payload"]
                    logger.info(f"[{worker_id}] Processing job {job_id}")
                    
                    try:
                        self.process_fn(job_id, payload, worker_id)
                        global_queue.ack("analysis_jobs", job_id)
                        logger.info(f"[{worker_id}] Successfully processed job {job_id}")
                    except Exception as e:
                        logger.error(f"[{worker_id}] Error processing job {job_id}: {e}")
                        # In a real app, check retries inside the processor or here
                        retries = payload.get("retries", 0)
                        if retries < settings.MAX_RETRIES:
                            payload["retries"] = retries + 1
                            global_queue.nack("analysis_jobs", job_id, requeue=True)
                        else:
                            global_queue.send_to_dlq("analysis_jobs", payload, str(e))
                else:
                    time.sleep(1) # idle sleep if no job found
            except Exception as e:
                logger.error(f"[{worker_id}] Unhandled loop error: {e}")
                time.sleep(1)
