from app.schemas import BookDTO
from app.schemas.book_copy import BookCopyDTO


class BookCopyRelationDTO(BookCopyDTO):
    book: BookDTO
