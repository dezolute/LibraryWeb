from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.models.types import Role
from app.schemas.request import RequestSemiRelationDTO


class UserUpdateDTO(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    email: EmailStr


class UserCreateDTO(UserUpdateDTO):
    password: Annotated[str, Field(min_length=8, max_length=64)]
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        password = info.data.get("password")
        if password != v:
            raise ValueError("Passwords do not match")
        return v


class UserDTO(UserUpdateDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    icon: Annotated[Optional[str], Field(default=None)]
    role: Role
    created_at: datetime
    verified: bool


class UserRelationDTO(UserDTO):
    requests: List[RequestSemiRelationDTO]