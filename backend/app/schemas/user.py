from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.types import Role, Status
from app.schemas import BookDTO


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
    requests: list["RequestSemiRelationDTO"]


class RequestDTO(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: Status
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RequestSemiRelationDTO(RequestDTO):
    book: BookDTO

class RequestRelationDTO(RequestSemiRelationDTO):
    user: UserDTO