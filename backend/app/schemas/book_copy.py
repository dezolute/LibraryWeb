from pydantic import BaseModel, ConfigDict

from app.models.types import BookAccessType, BookCopyStatus


class BookCopyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    serial_num: str
    status: BookCopyStatus
    access_type: BookAccessType