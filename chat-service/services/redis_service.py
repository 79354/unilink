import json
from typing import List, Optional
from core.redis_client import get_redis, get_redis_pub

# Redis key patterns
class REDIS_KEYS:
    @staticmethod
    def user_socket(user_id: str) -> str:
        return f"socket:user:{user_id}"
    
    @staticmethod
    def socket_user(socket_id: str) -> str:
        return f"socket:id:{socket_id}"
    
    @staticmethod
    def online_users() -> str:
        return "online:users"
    
    @staticmethod
    def typing(conversation_id: str) -> str:
        return f"typing:{conversation_id}"
    
    @staticmethod
    def message_cache(conversation_id: str) -> str:
        return f"messages:{conversation_id}"
    
    @staticmethod
    def unread_count(user_id: str, conversation_id: str) -> str:
        return f"unread:{user_id}:{conversation_id}"
    
    @staticmethod
    def total_unread(user_id: str) -> str:
        return f"unread:{user_id}:total"
    
    @staticmethod
    def user_presence(user_id: str) -> str:
        return f"presence:{user_id}"

# Redis Pub/Sub channels
class REDIS_CHANNELS:
    MESSAGE_NEW = "channel:message:new"
    TYPING_START = "channel:typing:start"
    TYPING_STOP = "channel:typing:stop"
    USER_ONLINE = "channel:user:online"
    USER_OFFLINE = "channel:user:offline"
    MESSAGE_READ = "channel:message:read"

# Notification channels
class NOTIFICATION_CHANNELS:
    MESSAGE = "notification:message"

class RedisService:
    @staticmethod
    async def set_user_socket(user_id: str, socket_id: str):
        redis = get_redis()
        pipe = redis.pipeline()
        pipe.set(REDIS_KEYS.user_socket(user_id), socket_id, ex=86400)
        pipe.set(REDIS_KEYS.socket_user(socket_id), user_id, ex=86400)
        await pipe.execute()
    
    @staticmethod
    async def get_user_socket(user_id: str) -> Optional[str]:
        redis = get_redis()
        return await redis.get(REDIS_KEYS.user_socket(user_id))
    
    @staticmethod
    async def get_socket_user(socket_id: str) -> Optional[str]:
        redis = get_redis()
        return await redis.get(REDIS_KEYS.socket_user(socket_id))
    
    @staticmethod
    async def remove_user_socket(user_id: str, socket_id: str):
        redis = get_redis()
        pipe = redis.pipeline()
        pipe.delete(REDIS_KEYS.user_socket(user_id))
        pipe.delete(REDIS_KEYS.socket_user(socket_id))
        await pipe.execute()
    
    @staticmethod
    async def set_user_online(user_id: str):
        redis = get_redis()
        pipe = redis.pipeline()
        pipe.sadd(REDIS_KEYS.online_users(), user_id)
        pipe.set(REDIS_KEYS.user_presence(user_id), str(int(1000)))
        await pipe.execute()
    
    @staticmethod
    async def set_user_offline(user_id: str):
        redis = get_redis()
        pipe = redis.pipeline()
        pipe.srem(REDIS_KEYS.online_users(), user_id)
        pipe.delete(REDIS_KEYS.user_presence(user_id))
        await pipe.execute()
    
    @staticmethod
    async def is_user_online(user_id: str) -> bool:
        redis = get_redis()
        return await redis.sismember(REDIS_KEYS.online_users(), user_id)
    
    @staticmethod
    async def get_online_users() -> List[str]:
        redis = get_redis()
        return await redis.smembers(REDIS_KEYS.online_users())
    
    @staticmethod
    async def get_online_friends(user_ids: List[str]) -> List[str]:
        if not user_ids:
            return []
        redis = get_redis()
        pipe = redis.pipeline()
        for user_id in user_ids:
            pipe.sismember(REDIS_KEYS.online_users(), user_id)
        results = await pipe.execute()
        return [user_ids[i] for i, result in enumerate(results) if result]
    
    @staticmethod
    async def set_typing(conversation_id: str, user_id: str):
        redis = get_redis()
        await redis.sadd(REDIS_KEYS.typing(conversation_id), user_id)
        await redis.expire(REDIS_KEYS.typing(conversation_id), 5)
    
    @staticmethod
    async def remove_typing(conversation_id: str, user_id: str):
        redis = get_redis()
        await redis.srem(REDIS_KEYS.typing(conversation_id), user_id)
    
    @staticmethod
    async def get_typing_users(conversation_id: str) -> List[str]:
        redis = get_redis()
        return await redis.smembers(REDIS_KEYS.typing(conversation_id))
    
    @staticmethod
    async def cache_message(conversation_id: str, message: dict):
        redis = get_redis()
        message_str = json.dumps(message, default=str)
        await redis.lpush(REDIS_KEYS.message_cache(conversation_id), message_str)
        await redis.ltrim(REDIS_KEYS.message_cache(conversation_id), 0, 49)
        await redis.expire(REDIS_KEYS.message_cache(conversation_id), 3600)
    
    @staticmethod
    async def get_cached_messages(conversation_id: str, count: int = 50) -> List[dict]:
        redis = get_redis()
        messages = await redis.lrange(REDIS_KEYS.message_cache(conversation_id), 0, count - 1)
        return [json.loads(msg) for msg in reversed(messages)]
    
    @staticmethod
    async def increment_unread(user_id: str, conversation_id: str):
        redis = get_redis()
        pipe = redis.pipeline()
        pipe.incr(REDIS_KEYS.unread_count(user_id, conversation_id))
        pipe.incr(REDIS_KEYS.total_unread(user_id))
        await pipe.execute()
    
    @staticmethod
    async def reset_unread(user_id: str, conversation_id: str):
        redis = get_redis()
        count = await redis.get(REDIS_KEYS.unread_count(user_id, conversation_id)) or 0
        pipe = redis.pipeline()
        pipe.delete(REDIS_KEYS.unread_count(user_id, conversation_id))
        pipe.decrby(REDIS_KEYS.total_unread(user_id), int(count))
        await pipe.execute()
    
    @staticmethod
    async def get_unread_count(user_id: str, conversation_id: str) -> int:
        redis = get_redis()
        count = await redis.get(REDIS_KEYS.unread_count(user_id, conversation_id))
        return int(count) if count else 0
    
    @staticmethod
    async def get_total_unread(user_id: str) -> int:
        redis = get_redis()
        count = await redis.get(REDIS_KEYS.total_unread(user_id))
        return int(count) if count else 0
    
    @staticmethod
    async def publish(channel: str, data: dict):
        redis_pub = get_redis_pub()
        await redis_pub.publish(channel, json.dumps(data, default=str))