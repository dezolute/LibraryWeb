import asyncio
import os
import secrets
from typing import Callable

from fastapi import UploadFile, HTTPException
from starlette import status

from app.models.types import Role
from app.modules import RedisRepository
from app.modules.email import send_verify_email
from app.modules.s3_files import upload_file_to_s3
from app.repositories import AbstractRepository
from app.schemas import UserDTO, UserCreateDTO, UserUpdateDTO
from app.utils import OAuth2Utility


class UserService:
    def __init__(self, user_repository: Callable[[], AbstractRepository]):
        self.user_repository: AbstractRepository = user_repository()
        self.redis: RedisRepository = RedisRepository()

    async def set_icon_to_user(self, user_id: int, file: UploadFile):
        ext = os.path.splitext(file.filename)[-1]
        path_to_file = os.path.join(os.path.abspath("."), "temp", f"new_icon{ext}")

        with open(path_to_file, 'wb') as f:
            f.write(await file.read())

        url = upload_file_to_s3(path_to_file)

        os.remove(path_to_file)

        book = await self.user_repository.update({"icon": url}, id=user_id)

        book_db = UserDTO.model_validate(book)
        return book_db

    async def get_orm_data(self, **kwargs):
        user = await self.user_repository.find(**kwargs)
        if user is None:
            raise HTTPException(status_code=404)

        return user

    async def set_verify_email_to_user(self, token: str) -> UserDTO:
        redis_email = await self.redis.get_verify_tokens(token)
        if not redis_email:
            raise HTTPException(status_code=404, detail="Email not found")

        await self.redis.delete_verify_tokens(token)

        verified_user = await self.user_repository.update({"verified": True}, email=redis_email)
        return UserDTO.model_validate(verified_user)

    async def add_user(self, user: UserCreateDTO) -> UserDTO:
        encrypted_password = OAuth2Utility.get_hashed_password(user.password)

        user_dict = user.model_dump()

        clear_user = UserUpdateDTO.model_validate(user_dict)
        user_dict = clear_user.model_dump()
        user_dict.update({"encrypted_password": encrypted_password})

        try:
            db_user = await self.user_repository.create(user_dict)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email alredy exist"
            )

        token = secrets.token_urlsafe(15)
        asyncio.create_task(send_verify_email(
            to=db_user.email,
            token=token
        ))
        await self.redis.set_verify_tokens(token_id=token, email=db_user.email)

        return UserDTO.model_validate(db_user)

    async def add_employee(self, employee: UserCreateDTO):
        employee_dict = employee.model_dump()
        employee_dict.update({
            "verify": True,
            "role": Role.EMPLOYEE
        })
        db_employee = await self.add_user(employee_dict)

        return UserDTO.model(db_employee)

    async def add_admin(self, admin: UserCreateDTO):
        admin_dict = admin.model_dump()
        admin_dict.update({
            "verify": True,
            "role": Role.ADMIN
        })
        db_admin = await self.add_user(admin_dict)

        return UserDTO.model_validate(db_admin)
