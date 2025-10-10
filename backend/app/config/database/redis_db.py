from contextlib import asynccontextmanager
from redis.asyncio import Redis

from app.config.database.redis_config import redis_config


class RedisConnection:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None

    async def __aenter__(self):
        self.redis = Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=True
        )
        return self.redis

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis:
            await self.redis.close()

class RedisDB:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db

    @asynccontextmanager
    async def get_connect(self):
        async with RedisConnection(
                host=self.host,
                port=self.port,
                db=self.db
        ) as conn:
            try:
                await conn.ping()
                yield conn
            finally:
                await conn.close()


redis_db = RedisDB(
    host=redis_config.REDIS_HOST,
    port=redis_config.REDIS_PORT,
    db=redis_config.REDIS_DB,
)