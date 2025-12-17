from typing import List, Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.types import BookAccessType

class BookCopyCreateDTO(BaseModel):
    serial_num: str
    access_type: BookAccessType

class BookClearDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Annotated[str, Field(max_length=100)]
    author: Annotated[str, Field(max_length=100)]
    publisher: Annotated[str, Field(max_length=100)]
    year_publication: int

class BookCreateDTO(BookClearDTO):
    copies: list[BookCopyCreateDTO]

class BookDTO(BookClearDTO):
    id: int
    cover_url: Optional[str]
