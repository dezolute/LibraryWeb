from datetime import datetime

from pydantic import BaseModel, ConfigDict

class LoanCreateDTO(BaseModel):
    reader_id: int
    book_id: int


class LoanDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reader_id: int
    copy_id: str
    issue_date: datetime
    due_date: datetime
    return_date: datetime | None