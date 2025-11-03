import asyncio
import os.path
from typing import List, Any, Coroutine

import aiohttp
from fastapi import HTTPException, UploadFile
from starlette import status

from app.models import BookCopyORM
from app.models.types import BookCopyStatus
from app.modules.s3 import upload_file_to_s3
from app.schemas import BookDTO, BookCreateDTO, MultiDTO, BookCopyCreateDTO, BookCopyDTO
from app.schemas.book_copy import BookCopyFullDTO
from app.schemas.relations import BookRelationDTO
from app.schemas.utils import Pagination
from app.schemas.utils.filters import BookFilter
from app.repositories import RepositoryType


async def notify(book_id: int, host: str):
    async with aiohttp.ClientSession() as session:
        await session.post(f"http://{host}/requests/notify", data=book_id)


class BookService:
    def __init__(
            self,
            book_repository: RepositoryType,
            book_copy_repository: RepositoryType
    ):
        self.book_repository: RepositoryType = book_repository
        self.book_copy_repository: RepositoryType = book_copy_repository


    async def get_single(self, **filters) -> BookRelationDTO:
        book = await self.book_repository.find(**filters)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        return BookRelationDTO.model_validate(book)

    async def get_multi(
            self, pg: Pagination, book_filters: BookFilter = None, **filters
    ) -> MultiDTO[BookRelationDTO]:
        books, total = await self.book_repository.find_all(
            pg=pg,
            conditions=book_filters.conditions,
            **filters
        )

        books_dto = MultiDTO(items=[BookRelationDTO.model_validate(row) for row in books], total=total)
        return books_dto

    async def add_book(self, book: BookCreateDTO) -> BookDTO:
        book_dict = book.model_dump()

        copy_list = book_dict.pop("copies")
        db_book = await self.book_repository.create(book_dict)
        copies = await self.book_copy_repository.create_multiple(
            [row | {"book_id": db_book.id} for row in copy_list]
        )
        db_book.copies = copies

        return BookRelationDTO.model_validate(db_book)

    async def add_multi(self, books: List[BookCreateDTO]) -> List[BookDTO]:
        books_dict = [row.model_dump() for row in books]
        db_books = await self.book_repository.create_multiple(books_dict)

        list_books_dto = [BookDTO.model_validate(row) for row in db_books]
        return list_books_dto

    async def update_book(self, book_id: int, host: str, book: BookCreateDTO) -> BookDTO:
        db_book = await self.book_repository.find(id=book_id)
        if db_book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        book_dict = book.model_dump()
        await self.book_repository.update(data=book_dict, id=book_id)
        updated_book = await self.book_repository.find(id=book_id)

        return BookRelationDTO.model_validate(updated_book)

    async def delete_book(self, book_id: int) -> BookDTO:
        book = await self.book_repository.delete(id=book_id)

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        return BookDTO.model_validate(book)

    async def set_cover_to_book(self, book_id: int, file: UploadFile) -> BookDTO:
        ext = os.path.splitext(file.filename)[-1]
        path_to_file = os.path.join(os.path.abspath("."), "temp", f"new_cover{ext}")

        with open(path_to_file, 'wb') as f:
            f.write(await file.read())

        url = upload_file_to_s3(path_to_file)

        with open(path_to_file, 'wb') as f:
            f.write(bytes(0))

        book = await self.book_repository.update(data={"cover_url": url}, id=book_id)

        book_db = BookDTO.model_validate(book)
        return book_db

    async def get_filtered_books(self, pg: Pagination, filters: BookFilter) -> MultiDTO[BookRelationDTO]:
        books, total = await self.book_repository.find_all(
            limit=pg.limit,
            offset=pg.offset,
            order_by=pg.order_by,
            condition=[
                filters.condition,
            ],
        )

        return MultiDTO(
            items=[BookRelationDTO.model_validate(row) for row in books],
            total=total,
        )

    async def add_copies(self, copies: List[BookCopyCreateDTO]) -> MultiDTO[BookRelationDTO]:
        copies_dict = [row.model_dump() for row in copies]
        copies = await self.book_repository.create_multiple(copies_dict)

        ids = [copy.serial_num  for copy in copies]
        books, total = await self.book_copy_repository.find_all(conditions=[
            BookCopyORM.serial_num.in_(ids)
        ])

        list_books_dto = [BookRelationDTO.model_validate(row) for row in books]
        return MultiDTO(items=list_books_dto, total=total)

    async def delete_copies(self, copies: List[str]) -> MultiDTO[BookCopyDTO]:
        db_copies = await self.book_copy_repository.delete(
            conditions=[BookCopyORM.serial_num.in_(copies)]
        )

        return MultiDTO(items=db_copies, total=len(copies))

    async def change_copy_status(self, new_status: BookCopyStatus, serial_num: str) -> BookCopyFullDTO:
        book_copy = await self.book_copy_repository.update(
            data={ "status": new_status },
            serial_num=serial_num,
            status=BookCopyStatus.RESERVED,
        )

        if book_copy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book copy not found",
            )

        return BookCopyFullDTO.model_validate(book_copy)
