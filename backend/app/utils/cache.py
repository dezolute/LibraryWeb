from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.config.database import redis_db, EnumRedisDB


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with redis_db.get_connect(EnumRedisDB.CACHE) as redis:
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        yield
