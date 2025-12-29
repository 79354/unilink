import redis.asyncio as aioredis
from app.core.config import settings
import json

redis_client: aioredis.Redis = None

class NotificationChannels:
    LIKE = "notification:like"
    MESSAGE = "notification:message"
    PROFILE_VIEW = "notification:profile-view"
    FRIEND_POST = "notification:friend-post"
    FRIEND_REQUEST = "notification:friend-request"

async def init_redis():
    global redis_client
    redis_client = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    print("✅ Redis connected")

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

def get_redis():
    return redis_client

async def publish_notification_event(channel: str, data: dict):
    try:
        await redis_client.publish(channel, json.dumps(data))
        print(f"📢 Published notification event to {channel}")
    except Exception as e:
        print(f"❌ Error publishing to {channel}: {e}")