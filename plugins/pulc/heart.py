import logging

import redis
import json
import time
from fastapi import FastAPI
from .env import REDIS_URL, WORKER_ID

app = FastAPI()
redis_client = redis.from_url(REDIS_URL)
logger = logging.getLogger(__name__)


def send_heartbeat():
    while True:
        heartbeat_message = {
            "worker_id": WORKER_ID,
            "timestamp": int(time.time()),
            "status": "healthy",
            "url": f"http://127.0.0.1:4556"
        }
        redis_client.publish("heartbeat_channel", json.dumps(heartbeat_message))
        logger.info(f"Sent heartbeat: {heartbeat_message}")
        time.sleep(5)
