from typing import TypeVar, Generic
from pydantic import BaseModel
from datetime import datetime
from app.models.types import Status
from app.schemas.book import BookDTO

UserDTO = TypeVar("UserDTO", bound=BaseModel)

class RequestDTO(BaseModel, Generic[UserDTO]):
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