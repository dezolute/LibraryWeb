from typing import List, Callable

from fastapi import HTTPException
from starlette import status

from app.models.types import Status
from app.repositories import AbstractRepository, BookRepository
from app.schemas import RequestDTO, RequestRelationDTO
from app.schemas.utils import Pagination
from app.services import BookService


class RequestService:
    def __init__(self, request_repository: Callable[[], AbstractRepository]):
        self.request_repository: AbstractRepository = request_repository()

    async def create_request(self, user_id: int, book_id: int):
        data = {
            "user_id": user_id,
            "book_id": book_id
        }
        book = await BookService(BookRepository).get_single(id=book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        db_request = await self.request_repository.create(data)

        return RequestDTO.model_validate(db_request)

    async def update_status(self, request_id: int, new_status: Status):
        data = {
            "status": new_status
        }

        request = await self.request_repository.update(data, id=request_id)

        return RequestDTO.model_validate(request)

    async def get_multi(self, pg: Pagination, **kwargs) -> List[RequestRelationDTO]:
        requests = await self.request_repository.find_all(
            limit=pg.limit,
            offset=pg.offset,
            order_by=pg.order_by,
            **kwargs
        )

        return [RequestRelationDTO.model_validate(row) for row in requests]

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