from pydantic import BaseModel


class BookCreateDTO(BaseModel):
    title: str
    author: str
    year: int

class BookDTO(BookCreateDTO):
    id: int

    class Config:
        from_attributes = True
