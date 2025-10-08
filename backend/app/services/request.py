import uuid
from typing import List, Callable

from fastapi import HTTPException
from starlette import status

from app.models.types import Status
from app.repositories import AbstractRepository, BookRepository
from app.schemas import RequestDTO, RequestRelationDTO, BookDTO, BookCreateDTO
from app.schemas.request import MultiRequestDTO
from app.schemas.utils import Pagination
from app.services import BookService


class RequestService:
    def __init__(self, request_repository: Callable[[], AbstractRepository]):
        self.request_repository: AbstractRepository = request_repository()

    async def create_request(self, user_id: int, book_id: int):
        data: dict[str, any] = {
            "user_id": user_id,
            "book_id": book_id
        }
        book_service = BookService(BookRepository)
        book = await book_service.get_single(id=book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        if book.count > 0:
            book_dto = BookCreateDTO.model_validate(book)
            book_dto.count -= 1
            await book_service.update_book(book_id=book_id, book=book_dto)
        else:
            data.update({'status': Status.in_queued})

        db_request = await self.request_repository.create(data)
        return RequestDTO.model_validate(db_request)

    async def update_status(self, request_id: int, new_status: Status):
        data = {
            "status": new_status
        }

        request = await self.request_repository.update(data, id=request_id)

        return RequestDTO.model_validate(request)

    async def get_multi(self, pg: Pagination, **kwargs) -> MultiRequestDTO:
        requests, total = await self.request_repository.find_all(
            limit=pg.limit,
            offset=pg.offset,
            order_by=pg.order_by,
            **kwargs
        )

        return MultiRequestDTO(items=[RequestRelationDTO.model_validate(row) for row in requests], total=total)

    async def get_single(self, request_id: int) -> RequestRelationDTO:
        request = await self.request_repository.find(id=request_id)

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        return RequestRelationDTO.model_validate(request)

    async def remove_request(self, request_id: int) -> RequestDTO:
        request = await self.request_repository.find(id=request_id)

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        return RequestDTO.model_validate(request)

    async def user_remove_request(self, request_id: int, user_id: int) -> RequestDTO:
        request = await self.request_repository.find(id=request_id , user_id=user_id)
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )
        if request.status == Status.accepted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Request already accepted, basic user can't remove it"
            )

        await self.request_repository.delete(
            id=request_id,
            user_id=user_id,
            status=Status.accepted
        )

        return RequestDTO.model_validate(request)