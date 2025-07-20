import os
import logging
from celery import Celery
from python_backend.logic import fetch_and_store_violations

# Configure logging for Celery worker
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "python_backend",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "fetch-and-store-violations-every-10-seconds": {
            "task": "python_backend.celery_bot.fetch_and_store_violations_task",
            "schedule": 10.0,
        },
    }
)

@celery_app.task
def fetch_and_store_violations_task():
    try:
        fetch_and_store_violations()
    except Exception as e:
        logger.error(f"Error in fetch_and_store_violations_task: {e}")
