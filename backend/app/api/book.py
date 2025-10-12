from typing import List, Annotated

from fastapi import APIRouter, Query, Depends, UploadFile, File

from app.deps import Deps
from app.models.types import Role
from app.schemas import UserRelationDTO, BookCreateDTO, BookDTO, MultiBookDTO
from app.schemas.utils import Pagination
from app.schemas.utils.filters import BookFilter
from app.services import BookService
from app.utils import OAuth2Utility
from app.utils.errors import Forbidden

book_router = APIRouter(
    tags=["Books"],
    prefix="/books",
)


@book_router.post("")
async def create_book(
    book: BookCreateDTO,
    book_service: Annotated[BookService, Depends(Deps.book_service)],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> BookDTO:
    if current_user.role == Role.USER:
        raise Forbidden

    db_book = await book_service.add_book(book)
    return db_book


@book_router.post("/multi")
async def create_multi(
    books: List[BookCreateDTO],
    book_service: Annotated[BookService, Depends(Deps.book_service)],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> List[BookDTO]:
    if current_user.role == Role.USER:
        raise Forbidden

    dto_books = await book_service.add_multi(books)
    return dto_books


@book_router.get("")
async def get_books(
    pg: Annotated[Pagination, Query()],
    book_service: Annotated[BookService, Depends(Deps.book_service)],
) -> MultiBookDTO:
    books = await book_service.get_multi(pg.limit, pg.offset, order_by=pg.order_by)
    return books


@book_router.get("/{book_id}")
async def get_book(
    book_id: int, book_service: Annotated[BookService, Depends(Deps.book_service)]
) -> BookDTO:
    book = await book_service.get_single(id=book_id)
    return book


@book_router.put("/{book_id}")
async def update_book(
    book_id: int,
    new_book: BookCreateDTO,
    book_service: Annotated[BookService, Depends(Deps.book_service)],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> BookDTO:
    if current_user.role == Role.USER:
        raise Forbidden

    updated_book = await book_service.update_book(book_id, new_book)
    return updated_book

@book_router.patch("/{book_id}")
async def set_book_cover(
    book_id: int,
    cover: Annotated[UploadFile, File()],
    book_service: Annotated[BookService, Depends(Deps.book_service)],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> BookDTO:
    if current_user.role == Role.USER:
        raise Forbidden

    covered_book = await book_service.set_cover_to_book(book_id, cover)
    return covered_book

@book_router.delete("/{book_id}")
async def delete_book(
    book_id: int, book_service: Annotated[BookService, Depends(Deps.book_service)],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> BookDTO:
    if current_user.role == Role.USER:
        raise Forbidden

    deleted_book = await book_service.delete_book(book_id)
    return deleted_book

@book_router.get("/filtered")
async def get_filtered_books(
    pg: Annotated[Pagination, Query()],
    filters: Annotated[BookFilter, Depends()],
    book_service: Annotated[BookService, Depends(Deps.book_service)],
) -> MultiBookDTO:
    filtered_books = await book_service.get_filtered_books(pg, filters)
    return filtered_books