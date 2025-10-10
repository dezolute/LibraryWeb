from typing import TypeVar, Generic

from app.config.database import redis_db

RefreshToken = TypeVar("RefreshToken", bound=str)

class RedisRepository:
    @staticmethod
    async def get_refresh_token(token_id) -> RefreshToken:
        async with redis_db.get_connect() as session:
            return await session.get(token_id)

    @staticmethod
    async def set_refresh_token(token_id, refresh_token) -> RefreshToken:
        async with redis_db.get_connect() as session:
            await session.set(token_id, refresh_token, ex=7*24*3600)
            return await session.get(token_id)