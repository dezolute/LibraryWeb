import asyncio
from datetime import datetime
from typing import Callable, List

from fastapi import HTTPException
from starlette import status

from app.models.types import Status
from app.modules.email import send_notification_email
from app.repositories import AbstractRepository, BookRepository
from app.schemas import RequestDTO, BookDTO, UserDTO, MultiRequestDTO, UserRelationDTO
from app.schemas.request import RequestRelationDTO
from app.schemas.utils import Pagination
from app.services import BookService
from app.repositories import UserRepository
from app.services import UserService


class RequestService:
    def __init__(self, request_repository: Callable[[], AbstractRepository]):
        self.request_repository: AbstractRepository = request_repository()
        self.book_service: BookService = BookService(BookRepository)
        self.user_service: UserService = UserService(UserRepository)

    @staticmethod
    def _to_relation_dto(row) -> RequestRelationDTO:
        dto_data = row.__dict__.copy()
        dto_data["user"] = UserDTO.model_validate(row.user).model_dump()
        dto_data["book"] = BookDTO.model_validate(row.book)
        return RequestRelationDTO.model_validate(dto_data)

    async def create_request(self, user_id: int, book_id: int) -> RequestDTO:
        data: dict[str, any] = {
            "user_id": user_id,
            "book_id": book_id
        }
        user = await self.user_service.get_orm_data(id=user_id)
        book = await self.book_service.get_single(id=book_id)

        user = UserRelationDTO.model_validate(user)
        for el in user.requests:
            if el.book.id == book_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You have this book in requests",
                )

        request_list = [el for el in user.requests if el.status != Status.RETURNED]
        if len(request_list) >= 5 :
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="You cannot request more than 5 requests",
            )

        if book.count == 0:
            data.update({'status': Status.IN_QUEUED})

        data.update({ 'status': Status.AWAITING })
        db_request = await self.request_repository.create(data)
        return RequestDTO.model_validate(db_request)

    async def update_status(self, request_id: int, new_status: Status) -> RequestDTO:
        data: dict[str, any] = {
            "status": new_status,
        }

        if new_status == Status.RETURNED or new_status == Status.GIVEN:
            request = await self.request_repository.find(id=request_id)
            if request is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            if new_status == Status.RETURNED:
                book_dto = BookDTO.model_validate(request.book)
                book_dto.count += 1
                await self.book_service.update_book(book_id=request.book_id, book=book_dto)

                data.update({'returned_at': datetime.now()})
            elif new_status == Status.GIVEN:
                book_dto = BookDTO.model_validate(request.book)
                book_dto.count -= 1
                await self.book_service.update_book(book_id=request.book_id, book=book_dto)

                data.update({'given_at': datetime.now()})

        request = await self.request_repository.update(data, id=request_id)

        return RequestDTO.model_validate(request)

    async def get_multi(self, pg: Pagination, **kwargs) -> MultiRequestDTO:
        requests, total = await self.request_repository.find_all(
            limit=pg.limit,
            offset=pg.offset,
            order_by=pg.order_by,
            **kwargs
        )

        items = [self._to_relation_dto(row) for row in requests]

        return MultiRequestDTO(items=items, total=total)

    async def get_single(self, request_id: int) -> RequestRelationDTO:
        request = await self.request_repository.find(id=request_id)

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        return RequestRelationDTO.model_validate(request)

    async def remove_request(self, request_id: int) -> RequestDTO:
        request = await self.request_repository.delete(id=request_id)

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        return RequestDTO.model_validate(request)

    async def user_remove_request(self, request_id: int, user_id: int) -> RequestDTO:
        request = await self.request_repository.find(id=request_id, user_id=user_id)
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )
        if request.status == Status.GIVEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Book already given, basic user can't remove it"
            )

        await self.request_repository.delete(
            id=request_id,
            user_id=user_id,
            status=Status.ACCEPTED
        )

        return RequestDTO.model_validate(request)

    async def send_notify(self, book_id: int) -> RequestDTO:
        request_list, _ = await self.request_repository.find_all(
            limit=1,
            offset=0,
            order_by='id',
            book_id=book_id,
            status=Status.IN_QUEUED
        )

        request = next(iter(request_list), None)
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        asyncio.create_task(send_notification_email(
            to=request.user.email,
            book_title=request.book.title,
        ))

        updated_request = await self.request_repository.update(
            data={"status": Status.AWAITING},
            id=request.id
        )

        return RequestDTO.model_validate(updated_request)

    async def get_overdue_requests(self, pg, **filters) -> List[RequestRelationDTO]:
        requests, total = await self.request_repository.find_overdue(
            limit=pg.limit,
            offset=pg.offset,
            order_by=pg.order_by,
            **filters
        )

        items = [self._to_relation_dto(row) for row in requests]

        return items
