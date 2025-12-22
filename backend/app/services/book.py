import asyncio
import os.path
from typing import List, Optional

import aiohttp
from fastapi import HTTPException, UploadFile
from starlette import status

from app.models import BookCopyORM
from app.models.types import BookCopyStatus, RequestStatus
from app.modules.s3 import upload_file_to_s3
from app.schemas import (
    BookDTO,
    BookCreateDTO,
    MultiDTO,
    BookCopyCreateDTO,
    BookCopyFullDTO,
    BookCopyDTO,
    BookClearDTO
)
from app.schemas.relations import BookRelationDTO
from app.schemas.utils import Pagination
from app.schemas.utils.filters import BookFilter
from app.repositories.sqlalchemy import SqlAlchemyRepository
from app.models.book import BookORM
from app.models.request import RequestORM
from app.modules.email.email_sender import send_notification_email


class BookService:
    def __init__(
            self,
            book_repository: SqlAlchemyRepository[BookORM],
            book_copy_repository: SqlAlchemyRepository[BookCopyORM],
            request_repository: SqlAlchemyRepository[RequestORM]
    ):
        self.book_repository: SqlAlchemyRepository[BookORM] = book_repository
        self.book_copy_repository: SqlAlchemyRepository[BookCopyORM] = book_copy_repository
        self.request_repository: SqlAlchemyRepository[RequestORM] = request_repository


    async def get_single(self, get_orm: bool = False, **filters) -> BookRelationDTO | BookORM:
        book = await self.book_repository.find(**filters)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )
        if get_orm:
            return book

        return BookRelationDTO.model_validate(book)

    async def get_multi(
            self, pg: Pagination, book_filters: Optional[BookFilter] = None, **filters
    ) -> MultiDTO[BookRelationDTO]:
        books, total = await self.book_repository.find_all(
            pg=pg,
            conditions=book_filters.conditions, # type: ignore
            **filters
        )

        books_dto = MultiDTO(items=[BookRelationDTO.model_validate(row) for row in books], total=total)
        return books_dto

    async def add_book(self, book: BookCreateDTO) -> BookDTO:
        book_dict = book.model_dump()

        copy_list = book_dict.pop("copies")
        db_book = await self.book_repository.create(book_dict)
        await self.book_copy_repository.create_multiple(
            [row | {"book_id": db_book.id} for row in copy_list]
        )

        book_dto: BookRelationDTO = await self.get_single(id=db_book.id) # type: ignore
        return book_dto

    async def add_multi(self, books: List[BookCreateDTO]) -> List[BookDTO]:
        books_dict = [row.model_dump() for row in books]
        db_books = await self.book_repository.create_multiple(books_dict)

        list_books_dto = [BookDTO.model_validate(row) for row in db_books]
        return list_books_dto

    async def update_book(self, book_id: int, book: BookClearDTO) -> BookDTO:
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
        ext = os.path.splitext(file.filename)[-1] # type: ignore
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
                filters.condition, # type: ignore
            ],
        )

        return MultiDTO(
            items=[BookRelationDTO.model_validate(row) for row in books],
            total=total,
        )

    async def add_copies(self, book_id: int, copies: List[BookCopyCreateDTO]) -> List[BookCopyFullDTO]:
        copies_dict = [row.model_dump() | { "book_id": book_id } for row in copies]
        copies_db = await self.book_copy_repository.create_multiple(copies_dict)

        list_books_dto = [BookCopyFullDTO.model_validate(row) for row in copies_db]
        return list_books_dto

    async def delete_copies(self, copies: List[str]) -> BookCopyDTO:
        db_copies = await self.book_copy_repository.delete(
            conditions=[BookCopyORM.serial_num.in_(copies)]
        )

        return BookCopyDTO.model_validate(db_copies)

    async def change_copy_status(self, new_status: BookCopyStatus, serial_num: str) -> BookCopyDTO:
        book_copy = await self.book_copy_repository.update(
            data={ "status": new_status },
            serial_num=serial_num,
        )

        if book_copy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book copy not found",
            )
        
        if new_status == BookCopyStatus.AVAILABLE:
            request = (await self.request_repository.find_all(
                pg=Pagination(
                    limit=1,
                    offset=0,
                    order_by="created_at"
                ),
                status=RequestStatus.QUEUED,
                book_id=book_copy.book_id
            ))[0]
            
            if len(request) != 0:
                await self.request_repository.update(
                    data={ "status": RequestStatus.PENDING },
                    id=request[0].id
                )
                
                db_copy = await self.change_copy_status(
                    new_status=BookCopyStatus.RESERVED,
                    serial_num=serial_num
                )
                
                _ = await asyncio.create_task(send_notification_email(
                    to=request[0].reader.email,
                    book_title=request[0].book.title,
                ))

                return BookCopyDTO.model_validate(db_copy)

        return BookCopyDTO.model_validate(book_copy)