from typing import Optional

import redis.asyncio as aioredis

from app.core.settings import settings


class RedisService:
    def __init__(self) -> None:
        self._pool: Optional[aioredis.Redis] = None

    def get_redis_client(self) -> aioredis.Redis:
        if self._pool is None:
            self._pool = aioredis.Redis.from_url(
                url=settings.redis.url,
                decode_responses=True,
            )
        return self._pool

    async def hset(self, name: str, **kwargs) -> None:
        client = await self.get_redis_client()

        async with client.pipeline() as pipe:
            await pipe.hset(name, mapping=kwargs)
            await pipe.expire(name, time=settings.redis.REDIS_TTL)
            await pipe.execute()

    async def hgetall(self, key: str) -> dict:
        client = await self.get_redis_client()
        return await client.hgetall(key)

    async def delete(self, name: str) -> bool:
        client = await self.get_redis_client()
        return await client.delete(name)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
