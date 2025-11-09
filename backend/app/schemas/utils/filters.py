from datetime import datetime, timedelta
from typing import Annotated, Optional, List, TypeVar, Type, Generic

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import ClauseElement

from app.models import BookORM, RequestORM, LoanORM


class BookFilter(BaseModel):
    author: Annotated[Optional[str], Query(None)]
    publisher: Annotated[Optional[str], Query(None)]
    year_publication: Annotated[Optional[int], Query(None)]

    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = []
        if self.author:
            conditions.append(BookORM.author.ilike(f"%{self.author}%"))
        if self.publisher:
            conditions.append(BookORM.publisher.ilike(f"%{self.publisher}%"))
        if self.year_publication:
            conditions.append(BookORM.year_publication == self.year_publication)

        return conditions


SqlModelType = TypeVar("SqlModelType")


class Filter[SqlModelType](BaseModel):
    book: Annotated[Optional[str], Query(None)]
    reader: Annotated[Optional[str], Query(None)]
    at: Annotated[Optional[datetime], Query(None)]
    to: Annotated[Optional[datetime], Query(default=datetime.now())]

    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = []

        if self.at and self.to:
            self.at = self.at.replace(tzinfo=None)
            self.to = self.to.replace(tzinfo=None)
            
        if self.at == self.to:
            self.to += timedelta(days=1)

        if self.book:
            conditions.append(SqlModelType.book.title.ilike(f"%{self.book}%"))
        if self.reader:
            conditions.append(SqlModelType.reader.profile.full_name.ilike(f"%{self.reader}%"))

        return conditions


class RequestFilter(Filter[RequestORM]):
    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = super().conditions
        if self.at and self.to:
            conditions.append(LoanORM.issue_date.between(self.at, self.to))

        return conditions


class LoanFilter(Filter[LoanORM]):
    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = super().conditions
        if self.at and self.to:
            conditions.append(LoanORM.issue_date.between(self.at, self.to))

        return conditions