from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class HistoryDTO(BaseModel):
    model_config =  ConfigDict(from_attributes=True)

    name: str
    borrowed_at: date
    borrowed_to: Optional[date]