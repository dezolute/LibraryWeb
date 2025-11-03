from typing import List, Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.types import BookAccessType

class BookCopyCreateDTO(BaseModel):
    serial_num: str
    access_type: BookAccessType

class BookCreateDTO(BaseModel):
    title: Annotated[str, Field(max_length=100)]
    author: Annotated[str, Field(max_length=100)]
    publisher: Annotated[str, Field(max_length=100)]
    year_publication: Annotated[int, Field(ge=1900)]
    copies: list[BookCopyCreateDTO]

class BookDTO(BookCreateDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cover_url: Optional[str]
    copies: None
