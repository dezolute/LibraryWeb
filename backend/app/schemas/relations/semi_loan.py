from app.schemas.loan import LoanDTO
from app.schemas.relations.book_copy import BookCopyRelationDTO


class LoanSemiRelationDTO(LoanDTO):
    book_copy: BookCopyRelationDTO