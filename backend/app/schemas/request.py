from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.types import RequestStatus


class RequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reader_id: Annotated[int, Field(ge=1)]
    book_id: Annotated[int, Field(ge=1)]
    status: RequestStatus
    created_at: datetime
