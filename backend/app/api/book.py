from typing import List, Annotated

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File
)
from fastapi_cache.decorator import cache

from app.api.types import BookServiceType, CurrentReaderType, PaginationType
from app.models.types import Role
from app.schemas import (
    BookCreateDTO,
    BookDTO,
    MultiDTO,
    BookCopyCreateDTO,
    BookCopyFullDTO,
)
from app.schemas.relations import BookRelationDTO
from app.schemas.utils import BookFilter
from app.utils.errors import Forbidden

book_router = APIRouter(
    tags=["Books"],
    prefix="/books",
)


@book_router.post("")
async def create_book(
        book: BookCreateDTO,
        current_reader: CurrentReaderType,
        book_service: BookServiceType,
) -> BookDTO:
    if current_reader.role == Role.READER:
        raise Forbidden

    db_book = await book_service.add_book(book)
    return db_book


@book_router.post("/multi")
async def create_multi(
        books: List[BookCreateDTO],
        current_reader: CurrentReaderType,
        book_service: BookServiceType,
) -> List[BookDTO]:
    if current_reader.role == Role.READER:
        raise Forbidden

    dto_books = await book_service.add_multi(books)
    return dto_books


@cache(expire=3600)
@book_router.get("")
async def get_books(
        pg: PaginationType,
        book_filters: Annotated[BookFilter, Depends()],
        book_service: BookServiceType,
) -> MultiDTO[BookRelationDTO]:
    books = await book_service.get_multi(pg, book_filters=book_filters)
    return books


@cache(expire=3600)
@book_router.get("/{book_id}")
async def get_book(
        book_id: int,
        book_service: BookServiceType
) -> BookRelationDTO:
    book: BookRelationDTO = await book_service.get_single(id=book_id) # type: ignore
    return book


@book_router.put("/{book_id}")
async def update_book(
        book_id: int,
        new_book: BookCreateDTO,
        book_service: BookServiceType,
        current_reader: CurrentReaderType,
) -> BookDTO:
    if current_reader.role == Role.READER:
        raise Forbidden

    updated_book = await book_service.update_book(book_id, new_book)
    return updated_book


@book_router.patch("/{book_id}")
async def set_book_cover(
        book_id: int,
        cover: Annotated[UploadFile, File()],
        current_reader: CurrentReaderType,
        book_service: BookServiceType,
) -> BookDTO:
    if current_reader.role == Role.READER:
        raise Forbidden

    covered_book = await book_service.set_cover_to_book(book_id, cover)
    return covered_book


@book_router.delete("/{book_id}")
async def delete_book(
        book_id: int,
        current_reader: CurrentReaderType,
        book_service: BookServiceType
) -> BookDTO:
    if current_reader.role == Role.READER:
        raise Forbidden

    deleted_book = await book_service.delete_book(book_id)
    return deleted_book

@book_router.post("/{book_id}/copies")
async def add_copies(
    book_id: int,
    copies: List[BookCopyCreateDTO],
    book_service: BookServiceType,
    current_reader: CurrentReaderType,
) -> List[BookCopyFullDTO]:
    if current_reader.role == Role.READER:
        raise Forbidden

    db_copies = await book_service.add_copies(book_id, copies)
    return db_copies