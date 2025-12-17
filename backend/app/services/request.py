import asyncio

from fastapi import HTTPException
from starlette import status

from app.models.types import RequestStatus, BookCopyStatus
from app.modules.email import send_notification_email
from app.repositories.factory import RepositoryType
from app.schemas import RequestDTO, MultiDTO
from app.schemas.relations import RequestRelationDTO, ReaderRelationDTO, RequestSemiRelationDTO
from app.schemas.utils import Pagination
from app.services.reader import ReaderService
from app.services.book import BookService
from app.schemas.loan import LoanCreateDTO
from app.services.loan import LoanService


class RequestService:
    def __init__(
            self,
            request_repository: RepositoryType, # type: ignore
            reader_service: ReaderService,
            book_service: BookService,
            loan_service: LoanService,
    ):
        self.request_repository: RepositoryType = request_repository # type: ignore
        self.book_service: BookService = book_service
        self.reader_service: ReaderService = reader_service
        self.loan_service: LoanService = loan_service

    async def create_request(self, reader_id: int, book_id: int) -> RequestDTO:
        data: dict[str, int] = {
            "reader_id": reader_id,
            "book_id": book_id
        }
        reader = await self.reader_service.get_orm_data(id=reader_id)

        reader = ReaderRelationDTO.model_validate(reader)
        for el in reader.requests:
            if el.book.id == book_id and el.status != RequestStatus.FULFILLED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You have this book in requests",
                )

        request_list = [el for el in reader.requests if el.status != RequestStatus.FULFILLED]
        if len(request_list) >= 5:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="You cannot request more than 5 requests",
            )

        book = await self.book_service.get_single(get_orm=True, id=book_id)
        new_status = {}
        for el in book.copies:
            if el.status == BookCopyStatus.AVAILABLE:
                await self.book_service.change_copy_status(
                    new_status=BookCopyStatus.RESERVED,
                    serial_num=el.serial_num
                )
                break
        else:
            new_status = { "status": RequestStatus.QUEUED }

        db_request = await self.request_repository.create(data | new_status)
        db_request.book = book

        return RequestSemiRelationDTO.model_validate(db_request)

    async def update_status(self, request_id: int, new_status: RequestStatus) -> RequestDTO:
        request = await self.request_repository.update(
            data={ "status": new_status },
            id=request_id
        )

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )

        return RequestDTO.model_validate(request)

    async def get_multi(
        self, pg: Pagination,
        conditions = None,
        **filters
    ) -> MultiDTO[RequestRelationDTO]:
        requests, total = await self.request_repository.find_all(
            pg=pg,
            conditions=conditions,
            **filters
        )

        requests_db = MultiDTO(
            items=[RequestRelationDTO.model_validate(row) for row in requests],
            total=total
        )
        return requests_db

    async def get_single(self, request_id: int) -> RequestRelationDTO:
        request = await self.request_repository.find(id=request_id)

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        return RequestRelationDTO.model_validate(request)

    async def reader_remove_request(self, request_id: int, reader_id: int) -> RequestDTO:
        request = await self.request_repository.delete(
            id=request_id,
            reader_id=reader_id,
            status=RequestStatus.QUEUED
        )

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        return RequestDTO.model_validate(request)

    async def send_notify(self, book_id: int) -> RequestDTO:
        request_list, _ = await self.request_repository.find_all(
            pg=Pagination(
                limit=1,
                offset=0,
                order_by="id",
            ),
            book_id=book_id,
            status=RequestStatus.QUEUED
        )

        request = next(iter(request_list), None)
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found"
            )

        asyncio.create_task(send_notification_email(
            to=request.reader.email,
            book_title=request.book.title,
        ))

        return RequestDTO.model_validate(request)

    async def give_book(self, request_id: int) -> RequestDTO:
        request = await self.update_status(
            request_id=request_id,
            new_status=RequestStatus.FULFILLED.value # type: ignore
        )

        await self.loan_service.create_loan(
            loan=LoanCreateDTO(
                reader_id=request.reader_id,
                book_id=request.book_id
            )
        )
    
        return request