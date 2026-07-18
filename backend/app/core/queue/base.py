from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class BaseQueue(ABC):
    @abstractmethod
    def enqueue(self, queue_name: str, payload: Dict[str, Any], priority: int = 0, request_id: str = None) -> str:
        """Push a job to the queue, returning a job_id. Supports priority and idempotency via request_id."""
        pass
        
    @abstractmethod
    def dequeue(self, queue_name: str, worker_id: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """Pull a job from the queue. Returns highest priority first."""
        pass
        
    @abstractmethod
    def heartbeat(self, queue_name: str, job_id: str, worker_id: str) -> None:
        """Worker heartbeat to signify it's still alive and processing."""
        pass
        
    @abstractmethod
    def ack(self, queue_name: str, job_id: str) -> None:
        """Acknowledge job completion."""
        pass
        
    @abstractmethod
    def nack(self, queue_name: str, job_id: str, requeue: bool = True) -> None:
        """Negative acknowledge, optionally requeueing the job."""
        pass
        
    @abstractmethod
    def send_to_dlq(self, queue_name: str, payload: Dict[str, Any], error: str) -> None:
        """Send job to Dead Letter Queue."""
        pass
        
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Return queue metrics."""
        pass
