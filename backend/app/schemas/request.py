from typing import List, Annotated, Literal, Any, Callable, Self
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from pydantic.main import IncEx

from app.models.types import Status
from app.schemas import BookDTO


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
    user: dict


class MultiRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[RequestRelationDTO]
    total: int