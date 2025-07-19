import os
from celery import Celery
from drone_rush.logic import fetch_and_store_violations

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


celery_app = Celery(
    "drone_rush",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.beat_schedule = {
    "fetch-and-store-violations-every-10-seconds": {
        "task": "drone_rush.celery_bot.fetch_and_store_violations_task",
        "schedule": 10.0,  # every 10 seconds
    },
}
celery_app.conf.timezone = "UTC"

@celery_app.task
def fetch_and_store_violations_task():
    try:
        fetch_and_store_violations()
    except Exception as e:
        print(f"Error in fetch_and_store_violations_task: {e}")
