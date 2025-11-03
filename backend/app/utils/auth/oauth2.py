from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status

import app.repositories
from app.config import auth_config
from app.repositories import RepositoryFactory
from app.schemas.relations import ReaderRelationDTO
from app.schemas.utils import Token


def get_repo():
    return app.repositories.RepositoryFactory


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
    def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()

        expire = (
            datetime.now(timezone.utc) + expires_delta if expires_delta else timedelta(minutes=15)
        )

        to_encode.update({
            "exp": expire,
        })
        encoded_jwt = jwt.encode(
            to_encode, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def get_tokens(data: dict) -> Token:
        return Token(
            access_token=OAuth2Utility.create_token(
                data=data,
                expires_delta=timedelta(minutes=30)
            ),
            token_type='Bearer'
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
    async def get_current_reader(token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALGORITHM]
            )

            db_reader = await RepositoryFactory.reader_repository().find(email=payload.get("sub"), verified=True)
            if db_reader is None:
                raise credentials_exception

            reader = ReaderRelationDTO.model_validate(db_reader)

        except jwt.InvalidTokenError:
            raise credentials_exception

        return reader
