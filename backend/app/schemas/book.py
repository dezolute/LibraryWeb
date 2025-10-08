from typing import List

from pydantic import BaseModel, Field

from app.models.types import Priority


class BookCreateDTO(BaseModel):
    title: str = Field(max_length=100)
    author: str = Field(max_length=100)
    priority: Priority
    count: int = Field(default=0)
    year_publication: int = Field(ge=2000)


class BookDTO(BookCreateDTO):
    id: int

    class Config:
        from_attributes = True

class MultiBookDTO(BaseModel):
    items: List[BookDTO]
    total: int
    class Config:
        from_attributes = True