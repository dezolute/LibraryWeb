from pydantic import BaseModel

class BookFilter(BaseModel):
    author: str | None = None
    publisher: str | None = None
    year_publication: int | None = None