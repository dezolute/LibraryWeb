from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, EmailStr, Field
from src.models.types import Role, Status
from src.schemas import BookDTO


class UserUpdateDTO(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr


class UserCreateDTO(UserUpdateDTO):
    password: str = Field(min_length=8, max_length=64)
    confirm_password: str


class UserDTO(UserUpdateDTO):
    id: int
    role: Role
    created_at: datetime
    requests: list["RequestDTO"] | None

    class Config:
        from_attributes = True


class RequestDTO(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: Status
    created_at: datetime
    updated_at: datetime

    user: UserDTO
    book: BookDTO

    class Config:
        from_attributes = True
