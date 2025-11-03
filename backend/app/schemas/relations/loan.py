from app.schemas import ReaderDTO
from app.schemas.loan import LoanDTO
from app.schemas.relations.book_copy import BookCopyRelationDTO


class LoanRelationDTO(LoanDTO):
    user: ReaderDTO
    book_copy: BookCopyRelationDTO
