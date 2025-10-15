from pydantic import BaseModel
from typing import Annotated, Optional
from fastapi import Query


class Pagination(BaseModel):
    limit: Annotated[int, Query(100)]
    offset: Annotated[int, Query(0)]
    order_by: Annotated[Optional[str], Query(None)]
