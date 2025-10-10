from typing import Callable

from dulwich.objects import is_commit
from fastapi import HTTPException, UploadFile
from passlib.context import CryptContext
from starlette import status

from app.modules.s3_files import upload_file_to_s3
from app.repositories import AbstractRepository
from app.schemas import UserCreateDTO, UserDTO, UserUpdateDTO
from app.schemas.utils import PairTokens
from app.utils.auth.oauth2 import OAuth2Utility
from app.modules import RedisRepository


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

    async def add_user(self, user: UserCreateDTO, file: UploadFile) -> UserDTO:
        encrypted_password = OAuth2Utility.get_hashed_password(user.password)

        url = upload_file_to_s3(file)

        user_dict = user.model_dump()

        clear_user = UserUpdateDTO.model_validate(user_dict)
        user_dict = clear_user.model_dump()
        user_dict.update(
            {
                "encrypted_password": encrypted_password,
                "icon": url
            }
        )

        db_user = await self.user_repository.create(user_dict)

        return UserDTO.model_validate(db_user)