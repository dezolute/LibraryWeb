import asyncio
from typing import Callable

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from app.modules import RedisRepository
from app.repositories import AbstractRepository
from app.schemas.utils import PairTokens
from app.utils.auth.oauth2 import OAuth2Utility


class AuthService:
    def __init__(self, user_repository: Callable[[], AbstractRepository]):
        self.user_repository: AbstractRepository = user_repository()
        self.redis: RedisRepository = RedisRepository()
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

        token = OAuth2Utility.get_tokens(
            data={
                "sub": user.email,
                "name": user.name,
            }
        )

        return token