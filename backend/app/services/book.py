import os.path
from typing import Callable, List

import aiohttp
from fastapi import HTTPException, UploadFile
from starlette import status

from app.modules.s3_files import upload_file_to_s3
from app.repositories.base_repository import AbstractRepository
from app.schemas import BookDTO, BookCreateDTO, MultiBookDTO
from app.schemas.utils import Pagination
from app.schemas.utils.filters import BookFilter

API_URL = "http://localhost/api"


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
            async with aiohttp.ClientSession() as session:
                await session.post(f"{API_URL}/requests/notify", data=book_id)

        return updated_book

    async def delete_book(self, book_id: int) -> BookDTO:
        book = await self.book_repository.delete(id=book_id)

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        return BookDTO.model_validate(book)

    async def set_cover_to_book(self, book_id: int, file: UploadFile) -> BookDTO:
        path_to_file = f'{os.path.abspath('.')}\\temp\\new_cover.{file.filename.split('.')[-1]}'
        with open(path_to_file, 'wb') as f:
            f.write(await file.read())

        url = upload_file_to_s3(path_to_file)

        with open(path_to_file, 'wb') as f:
            f.write(bytes(0))

        book = await self.book_repository.update({ "cover": url }, id=book_id)

        book_db = BookDTO.model_validate(book)
        return book_db

    async def get_filtered_books(self, pg: Pagination, filters: BookFilter) -> MultiBookDTO:
        books, total = self.book_repository.find_books(
            limit=pg.limit,
            offset=pg.offset,
            order_by=pg.order_by,
            filters=filters
        )

        return MultiBookDTO(
            items=[BookDTO.model_validate(row) for row in books],
            total=total,
        )