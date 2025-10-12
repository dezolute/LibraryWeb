from typing import Callable

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from app.config.database import RedisEnum
from app.repositories import AbstractRepository
from app.schemas.utils import PairTokens
from app.utils.auth.oauth2 import OAuth2Utility
from app.modules import RedisRepository


class AuthService:
    def __init__(self, user_repository: Callable[[], AbstractRepository]):
        self.user_repository: AbstractRepository = user_repository()
        self.redis: RedisRepository = RedisRepository(RedisEnum.TOKENS)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def login(self, form_data) -> PairTokens:
        error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = await self.user_repository.find(email=form_data.username)
        if user is None:
            raise error

        is_compair = OAuth2Utility.verify_password(
            form_data.password, user.encrypted_password
        )

        if not is_compair:
            raise error

        tokens = OAuth2Utility.get_tokens(
            data={
                "sub": user.email,
                "name": user.name,
            }
        )

        await self.redis.set_refresh_token(token_id=tokens.token_id, refresh_token=tokens.refresh_token)

        return tokens

    async def refresh_tokens(self, refresh_token) -> PairTokens:
        payload = OAuth2Utility.get_token_payload(refresh_token)
        data = {
            "sub": payload["sub"],
            "name": payload["name"],
        }
        tokens = OAuth2Utility.get_tokens(data=data)
        await self.redis.set_refresh_token(tokens.token_id, tokens.refresh_token)

        return tokens