from typing import TypeVar

from app.config.database import redis_db

RefreshToken = TypeVar("RefreshToken", bound=str)

class RedisRepository:
    async def set_verify_tokens(self, token_id, email):
        async with redis_db.get_connect() as session:
            success = await session.set(token_id, email, ex=10 * 60)
            if success:
                return await session.get(token_id)
            return None

    async def get_verify_tokens(self, token_id):
        async with redis_db.get_connect() as session:
            email = await session.get(token_id)
            return email

    async def delete_verify_tokens(self, token_id):
        async with redis_db.get_connect() as session:
            email = await session.get(token_id)
            await session.delete(token_id)
            return email
