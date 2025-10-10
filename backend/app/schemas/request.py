from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.types import Status
from app.schemas.book import BookDTO

class UserDTO(BaseModel):
    pass

class RequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    book_id: int
    status: Status
    created_at: datetime
    updated_at: datetime



class RequestSemiRelationDTO(RequestDTO):
    book: BookDTO


class RequestRelationDTO(RequestSemiRelationDTO):
    user: UserDTO


class MultiRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[RequestRelationDTO]
    total: int