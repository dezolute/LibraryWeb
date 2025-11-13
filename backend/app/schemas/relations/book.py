from typing import List

from app.schemas.book import BookDTO
from app.schemas.book_copy import BookCopyDTO


class BookRelationDTO(BookDTO):
    copies: List[BookCopyDTO]
