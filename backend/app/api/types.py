from typing import Annotated

from fastapi import Depends, Query

from app.deps import Deps
from app.schemas.relations import ReaderRelationDTO
from app.schemas.utils import Pagination
from app.services import RequestService, ReaderService, BookService, LoanService
from app.utils import OAuth2Utility

PaginationType = Annotated[Pagination, Query()]
CurrentReaderType = Annotated[ReaderRelationDTO, Depends(OAuth2Utility.get_current_reader)]

RequestServiceType = Annotated[RequestService, Depends(Deps.request_service)]
ReaderServiceType = Annotated[ReaderService, Depends(Deps.reader_service)]
BookServiceType = Annotated[BookService, Depends(Deps.book_service)]
LoanServiceType = Annotated[LoanService, Depends(Deps.loan_service)]