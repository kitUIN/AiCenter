import json

import redis
from django.core.management.base import BaseCommand

from application.settings import REDIS_URL
from center.models import Worker


class Command(BaseCommand):
    help = "Consume heartbeats from Redis"

    def handle(self, *args, **options):
        redis_client = redis.from_url(REDIS_URL)
        pubsub = redis_client.pubsub()
        pubsub.subscribe('heartbeat_channel')

        print("Listening for heartbeats...")
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    worker_id = data['worker_id']
                    timestamp = data['timestamp']

                    # 更新或创建工作节点记录
                    worker, created = Worker.objects.update_or_create(
                        id=worker_id,
                        defaults={"last_heartbeat": timestamp, "status": "healthy"}
                    )
                    print(f"Updated heartbeat for {worker_id} at {timestamp}")
                except Exception as e:
                    print(f"Error processing message: {e}")
