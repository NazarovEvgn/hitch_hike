import redis.asyncio as aioredis
from app.core.config import settings


class RedisClient:
    """Redis client for caching and pub/sub."""

    def __init__(self):
        self.redis: aioredis.Redis | None = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> str | None:
        """Get value by key."""
        if self.redis:
            return await self.redis.get(key)
        return None

    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value with expiration."""
        if self.redis:
            await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        """Delete key."""
        if self.redis:
            await self.redis.delete(key)


redis_client = RedisClient()
