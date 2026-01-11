from app.schemas import BookDTO
from app.schemas.book_copy import BookCopyDTO
from app.schemas.history import HistoryDTO


class BookCopyRelationDTO(BookCopyDTO):
    book: BookDTO