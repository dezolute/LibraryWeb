from typing import Annotated

from pydantic import Field

from app.schemas.reader import ReaderDTO
from app.schemas.request import RequestDTO
from app.schemas.loan import LoanDTO
from app.schemas.profile import ProfileDTO
from app.schemas.book import BookDTO
from app.schemas.relations.book_copy import BookCopyRelationDTO


class RequestSemiRelationDTO(RequestDTO):
    book: BookDTO


class LoanSemiRelationDTO(LoanDTO):
    book_copy: BookCopyRelationDTO


class ReaderSemiRelationDTO(ReaderDTO):
    profile: ProfileDTO

class ReaderRelationDTO(ReaderSemiRelationDTO):
    requests: Annotated[list[RequestSemiRelationDTO], Field(default=[])]
    loans: Annotated[list[LoanSemiRelationDTO], Field(default=[])]