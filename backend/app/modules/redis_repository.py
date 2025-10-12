from typing import TypeVar

from app.config.database import redis_db, RedisEnum


RefreshToken = TypeVar("RefreshToken", bound=str)


# TODO: refactoring logic | methods
class RedisRepository:
    def __init__(self, db: RedisEnum) -> None:
        self.db = db

    async def get_refresh_token(self, token_id) -> RefreshToken:
        async with redis_db.get_connect(db=self.db) as session:
            return await session.get(token_id)

    async def set_refresh_token(self, token_id, refresh_token) -> RefreshToken:
        async with redis_db.get_connect(db=self.db) as session:
            await session.set(token_id, refresh_token, ex=7*24*3600)

            return await session.get(token_id)

    async def delete_refresh_token(self, token_id):
        async with redis_db.get_connect(db=self.db) as session:
            refresh_token = await session.get(token_id)
            await session.delete(token_id)

            return refresh_token

    async def set_verify_tokens(self, token_id, email):
        async with redis_db.get_connect(db=self.db) as session:
            success = await session.set(token_id, email, ex=10 * 60)
            if success:
                return await session.get(token_id)
            return None

    async def get_verify_tokens(self, token_id):
        async with redis_db.get_connect(db=self.db) as session:
            email = await session.get(token_id)
            return email

    async def delete_verify_tokens(self, token_id):
        async with redis_db.get_connect(db=self.db) as session:
            email = await session.get(token_id)
            await session.delete(token_id)
            return email