from app.core.config import settings
from .memory import MemoryQueue

# In a real app, this might switch between RedisQueue, KafkaQueue, etc. based on settings.QUEUE_TYPE
# For now, we use MemoryQueue as the base implementation.

global_queue = MemoryQueue(
    max_workers=settings.WORKER_COUNT,
    heartbeat_timeout=settings.HEARTBEAT_TIMEOUT_SEC
)
