from typing import Callable, List

from fastapi import HTTPException
from starlette import status
from app.repositories.base_repository import AbstractRepository
from app.schemas.book import BookDTO, BookCreateDTO, MultiBookDTO


class BookService:
    def __init__(self, book_repository: Callable[[], AbstractRepository]):
        self.book_repository: AbstractRepository = book_repository()

    async def get_single(self, **filters) -> BookDTO:
        book = await self.book_repository.find(**filters)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        return BookDTO.model_validate(book)

    async def get_multi(
        self, limit: int, offset: int, order_by: str, **filters
    ) -> MultiBookDTO:
        books, total = await self.book_repository.find_all(
            limit=limit, offset=offset, order_by=order_by, **filters
        )

        books_dto = MultiBookDTO(items=[BookDTO.model_validate(row) for row in books], total=total)
        return books_dto

    async def add_book(self, book: BookCreateDTO) -> BookDTO:
        book_dict = book.model_dump()
        book = await self.book_repository.create(book_dict)

        return BookDTO.model_validate(book)

    async def add_multi(self, books: List[BookCreateDTO]) -> List[BookDTO]:
        books_dict = [row.model_dump() for row in books]
        db_books = await self.book_repository.create_multiple(books_dict)

        list_books_dto = [BookDTO.model_validate(row) for row in db_books]
        return list_books_dto

    async def update_book(self, book_id: int, book: BookCreateDTO) -> BookDTO:
        db_book = await self.book_repository.find(id=book_id)
        if db_book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        book_dict = book.model_dump()
        updated_book = await self.book_repository.update(book_dict, id=book_id)
        updated_book = BookDTO.model_validate(updated_book)
        if db_book.count == 0 and book.count != 0:
            pass

        return updated_book

    async def delete_book(self, book_id: int) -> BookDTO:
        book = await self.book_repository.delete(id=book_id)

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        return BookDTO.model_validate(book)
