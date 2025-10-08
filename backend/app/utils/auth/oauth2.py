import uuid
from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status

from app.config import auth_config
from app.repositories import UserRepository
from app.schemas.user import UserRelationDTO


class OAuth2Utility:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_hashed_password(cls, plain_password: str) -> str:
        return cls.pwd_context.hash(plain_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()

        expire = (
            datetime.now(timezone.utc) + expires_delta if expires_delta else timedelta(minutes=15)
        )

        to_encode.update({
            "exp": expire,
            "type": "access-token",
            "jti": str(uuid.uuid4()),
        })
        encoded_jwt = jwt.encode(
            to_encode, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()

        expire = (
            datetime.now(timezone.utc) + expires_delta if expires_delta else timedelta(minutes=15)
        )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode()

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
