from typing import List, Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.types import Priority


class BookCreateDTO(BaseModel):
    title: Annotated[str, Field(max_length=100)]
    author: Annotated[str, Field(max_length=100)]
    priority: Priority
    count: Annotated[int, Field(default=0)]
    year_publication: Annotated[int, Field(ge=1900)]


class BookDTO(BookCreateDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cover: Optional[str]


class MultiBookDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[BookDTO]
    total: int