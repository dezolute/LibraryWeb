from contextlib import asynccontextmanager
from enum import Enum

from redis.asyncio import Redis

from app.config.database.redis_config import redis_config


class EnumRedisDB(int, Enum):
    CACHE = 0,
    VERIFY = 1


class RedisConnection:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.redis = None

    async def __aenter__(self):
        self.redis = Redis(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            db=self.db,
            decode_responses=True
        )
        return self.redis

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis:
            await self.redis.close()


class RedisDB:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @asynccontextmanager
    async def get_connect(self, db: EnumRedisDB = EnumRedisDB.VERIFY):
        async with RedisConnection(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=db.value
        ) as conn:
            try:
                await conn.ping()
                yield conn
            finally:
                await conn.close()


redis_db = RedisDB(
    host=redis_config.REDIS_HOST,
    port=redis_config.REDIS_PORT,
    user=redis_config.REDIS_USER,
    password=redis_config.REDIS_PASSWORD
)
