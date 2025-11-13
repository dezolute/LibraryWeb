from datetime import datetime, timedelta
from typing import Annotated, Optional, List, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import ClauseElement

from app.models import BookORM, RequestORM, LoanORM
from app.models.types import RequestStatus


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


class Filter(BaseModel):
    book: Annotated[Optional[str], Query(None)]
    reader: Annotated[Optional[str], Query(None)]
    at: Annotated[Optional[datetime], Query(None)]
    to: Annotated[Optional[datetime], Query(None)]

    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = []

        if self.at and self.to:
            self.at = self.at.replace(tzinfo=None)
            self.to = self.to.replace(tzinfo=None)

            if self.at == self.to:
                self.to += timedelta(days=1)

        return conditions


class RequestFilter(Filter):
    status: Annotated[Optional[RequestStatus], Query(None)]

    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = super().conditions

        if self.book:
            conditions.append(RequestORM.book.title.ilike(f"%{self.book}%"))
        if self.reader:
            conditions.append(RequestORM.reader.profile.full_name.ilike(f"%{self.reader}%"))

        if self.at and self.to:
            conditions.append(RequestORM.created_at.between(self.at, self.to))
        if self.status:
            conditions.append(RequestORM.status == self.status.value)

        return conditions


class LoanFilter(Filter):
    @property
    def conditions(self) -> List[ClauseElement]:
        conditions = super().conditions
        if self.book:
            conditions.append(LoanORM.book_copy.book.title.ilike(f"%{self.book}%"))
        if self.reader:
            conditions.append(LoanORM.reader.profile.full_name.ilike(f"%{self.reader}%"))

        if self.at and self.to:
            conditions.append(LoanORM.issue_date.between(self.at, self.to))

        return conditions