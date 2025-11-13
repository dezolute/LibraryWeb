from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.models.types import Role


class ReaderUpdateDTO(BaseModel):
    full_name: Annotated[str, Field(max_length=100, pattern=r"^([А-Я]{1}[а-я]+ ){2}[А-Я]{1}[а-яА-Я]+$")]
    email: EmailStr


class ReaderCreateDTO(ReaderUpdateDTO):
    password: Annotated[str, Field(min_length=8, max_length=64)]
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        password = info.data.get("password")
        if password != v:
            raise ValueError("Passwords do not match")
        return v


class ReaderDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    verified: bool

