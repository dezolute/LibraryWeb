from datetime import datetime
from typing import List, Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.types import Status
from app.schemas import BookDTO


class RequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Annotated[int, Field(ge=1)]
    book_id: Annotated[int, Field(ge=1)]
    status: Status
    given_at: Annotated[Optional[datetime], Field(None)]
    returned_at: Annotated[Optional[datetime], Field(None)]
    created_at: datetime


class RequestSemiRelationDTO(RequestDTO):
    book: BookDTO


class RequestRelationDTO(RequestSemiRelationDTO):
    user: dict


class MultiRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[RequestRelationDTO]
    total: int
