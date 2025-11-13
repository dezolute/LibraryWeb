from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from app.schemas.utils import Token
from app.repositories import RepositoryType
from app.utils.auth.oauth2 import OAuth2Utility


class AuthService:
    def __init__(self, reader_repository: RepositoryType):
        self.reader_repository: RepositoryType = reader_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def login(self, form_data) -> Token:
        error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

        reader = await self.reader_repository.find(email=form_data.username)
        if reader is None or reader.profile is None:
            raise error

        is_compair = OAuth2Utility.verify_password(
            form_data.password, reader.encrypted_password
        )

        if not is_compair:
            raise error

        token = OAuth2Utility.get_tokens(
            data={
                "sub": reader.email,
                "full_name": reader.profile.full_name,
            }
        )

        return token
