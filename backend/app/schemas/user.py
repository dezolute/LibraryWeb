from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.types import Role
from app.schemas.request import RequestSemiRelationDTO


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

    class Config:
        from_attributes = True

class UserRelationDTO(UserDTO):
    requests: list[RequestSemiRelationDTO]