from typing import List, Annotated

from fastapi import APIRouter, Query, Depends

from app.deps import Deps
from app.models.types import Role
from app.schemas import UserDTO, RequestDTO, UserRelationDTO
from app.schemas.book import BookCreateDTO, BookDTO, MultiBookDTO
from app.schemas.utils import Pagination
from app.services import BookService
from app.services.request import RequestService
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
    # current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> BookDTO:
    # if current_user.role == Role.employee or current_user.role == Role.admin:
    db_book = await book_service.add_book(book)
    return db_book
    # else:
    #     raise Forbidden


@book_router.post("/multi")
async def create_multi(
    books: List[BookCreateDTO],
    book_service: Annotated[BookService, Depends(Deps.book_service)],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> List[BookDTO]:
    if current_user.role == Role.employee or current_user.role == Role.admin:
        dto_books = await book_service.add_multi(books)
        return dto_books
    else:
        raise Forbidden


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


@book_router.put("/{id}")
async def update_book(
    book_id: int,
    new_book: BookCreateDTO,
    book_service: Annotated[BookService, Depends(Deps.book_service)],
) -> BookDTO:
    updated_book = await book_service.update_book(book_id, new_book)
    return updated_book


@book_router.delete("/{id}")
async def delete_book(
    book_id: int, book_service: Annotated[BookService, Depends(Deps.book_service)]
) -> BookDTO:
    deleted_book = await book_service.delete_book(book_id)
    return deleted_book


@book_router.post("/requests")
async def create_request(
    book_id: int,
    current_user: Annotated[UserDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)]
) -> RequestDTO:
    request = await request_service.create_request(book_id, current_user.id)
    return request