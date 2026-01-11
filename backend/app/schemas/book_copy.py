from pydantic import BaseModel, ConfigDict

from app.models.types import BookAccessType, BookCopyStatus
from app.schemas.history import HistoryDTO


class BookCopyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    serial_num: str
    status: BookCopyStatus
    access_type: BookAccessType

class BookCopyHistoryDTO(BookCopyDTO):
    histories: list[HistoryDTO] = []

class BookCopyFullDTO(BookCopyDTO):
    book_id: int