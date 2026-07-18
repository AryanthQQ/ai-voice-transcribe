import sys
import time
from app.core.logger import logger
from app.workers.pool import WorkerPool
from app.workers.processor import process_job

def main():
    logger.info("Starting isolated Worker Service...")
    
    pool = WorkerPool(process_fn=process_job)
    
    try:
        pool.start()
        logger.info("Worker Service is running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received exit signal.")
        pool.stop()
        logger.info("Worker Service stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
