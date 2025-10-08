from datetime import timedelta
from typing import Callable

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from app.repositories import AbstractRepository
from app.schemas import UserCreateDTO, UserDTO, UserUpdateDTO
from app.schemas.utils import Token
from app.utils.auth.oauth2 import OAuth2Utility


class AuthService:
    def __init__(self, user_repository: Callable[[], AbstractRepository]):
        self.user_repository: AbstractRepository = user_repository()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def login(self, form_data) -> Token:
        error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = await self.user_repository.find(email=form_data.username)
        print(user)
        if user is None:
            raise error
        is_compair = OAuth2Utility.verify_password(
            form_data.password, user.encrypted_password
        )
        if not is_compair:
            raise error

        access_token = OAuth2Utility.create_access_token(
            data={
                "sub": user.email,
                "name": user.name,
            },
            expires_delta=timedelta(minutes=30),
        )

        return Token(access_token=access_token, token_type="bearer")

    async def add_user(self, user: UserCreateDTO) -> UserDTO:
        if user.password != user.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passwords do not match",
            )

        user_dict = user.model_dump()
        encrypted_password = OAuth2Utility.get_hashed_password(
            user_dict.get("password")
        )

        clear_user = UserUpdateDTO.model_validate(user_dict)
        user_dict = clear_user.model_dump()
        user_dict.setdefault("encrypted_password", encrypted_password)

        db_user = await self.user_repository.create(user_dict)

        return UserDTO.model_validate(db_user)
