import redis.asyncio as redis
from config.settings import settings

redis_client: redis.Redis = None
redis_pub: redis.Redis = None
redis_sub: redis.Redis = None

async def connect_to_redis():
    global redis_client, redis_pub, redis_sub
    
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=50
    )
    
    redis_pub = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    
    redis_sub = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    
    await redis_client.ping()
    print("Redis connected")

async def close_redis_connection():
    global redis_client, redis_pub, redis_sub
    if redis_client:
        await redis_client.close()
    if redis_pub:
        await redis_pub.close()
    if redis_sub:
        await redis_sub.close()
    print("Disconnected from Redis")

def get_redis():
    return redis_client

def get_redis_pub():
    return redis_pub

def get_redis_sub():
    return redis_sub