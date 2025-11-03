from typing import Annotated, Optional, List

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import ClauseElement

from app.models import BookORM

class BookFilter(BaseModel):
    author: Annotated[Optional[str], Query(None)]
    publisher: Annotated[Optional[str], Query(None)]
    year_publication: Annotated[Optional[int], Query(None)]

    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = []
        if self.author:
            conditions.append(BookORM.author.ilike(self.author))
        if self.publisher:
            conditions.append(BookORM.publisher.ilike(self.publisher))
        if self.year_publication:
            conditions.append(BookORM.year_publication == self.year_publication)

        return conditions
