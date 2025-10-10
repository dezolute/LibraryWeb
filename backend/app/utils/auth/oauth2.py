import uuid
from datetime import timedelta, datetime, timezone
from enum import Enum
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status

from app.config import auth_config
from app.repositories import UserRepository
from app.schemas.user import UserRelationDTO
from app.schemas.utils.token import PairTokens


class TokenType(Enum):
    ACCESS_TOKEN = "access-token"
    REFRESH_TOKEN = "refresh-token"


class OAuth2Utility:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth", refreshUrl="auth/refresh")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_hashed_password(cls, plain_password: str) -> str:
        return cls.pwd_context.hash(plain_password)

    @staticmethod
    def create_token(data: dict, token_type: TokenType, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()

        expire = (
            datetime.now(timezone.utc) + expires_delta if expires_delta else timedelta(minutes=15)
        )

        to_encode.update({
            "exp": expire,
            "type": token_type.value,
        })
        encoded_jwt = jwt.encode(
            to_encode, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def get_tokens(data: dict) -> PairTokens:
        token_id = str(uuid.uuid4())
        data.update({
            "jti": token_id,
        })
        return PairTokens(
            refresh_token=OAuth2Utility.create_token(
                data=data,
                token_type=TokenType.REFRESH_TOKEN,
                expires_delta=timedelta(days=7)
            ),
            access_token=OAuth2Utility.create_token(
                data=data,
                token_type=TokenType.ACCESS_TOKEN,
                expires_delta=timedelta(minutes=15)
            ),
            token_id=token_id
        )

    @staticmethod
    def get_token_payload(token: str) -> dict:
        try:
            payload = jwt.decode(
                token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALGORITHM]
            )

            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad token",
        )

    @staticmethod
    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALGORITHM]
            )

            db_user = await UserRepository().find(email=payload.get("sub"))
            user = UserRelationDTO.model_validate(db_user)

            if user is None:
                raise credentials_exception
        except jwt.InvalidTokenError:
            raise credentials_exception

        return user
