from fastapi import Query
from typing import Annotated, Optional

from pydantic import BaseModel


class BookFilter(BaseModel):
    author: Annotated[Optional[str], Query(None)]
    publisher: Annotated[Optional[str], Query(None)]
    year_publication: Annotated[Optional[int], Query(None)]
