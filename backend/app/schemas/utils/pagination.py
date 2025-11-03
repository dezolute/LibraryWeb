from typing import Annotated, Optional, Dict

from fastapi import Query
from pydantic import BaseModel


class Pagination(BaseModel):
    limit: Annotated[int, Query(100)]
    offset: Annotated[int, Query(0)]
    order_by: Annotated[Optional[str], Query("id")]

