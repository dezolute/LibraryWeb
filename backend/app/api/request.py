from typing import Annotated, List

from fastapi import APIRouter
from fastapi.params import Query, Body

from app.api.types import PaginationType, CurrentReaderType, RequestServiceType
from app.models.types import Role, RequestStatus
from app.schemas import RequestDTO, MultiDTO
from app.schemas.relations import RequestRelationDTO
from app.schemas.utils import Pagination
from app.utils.errors import Forbidden

request_router = APIRouter(
    prefix="/requests",
    tags=["Requests"]
)


@request_router.get("")
async def get_requests(
        pagination: PaginationType,
        current_reader: CurrentReaderType,
        request_service: RequestServiceType,
) -> MultiDTO[RequestRelationDTO]:
    if current_reader.role == Role.READER:
        raise Forbidden

    requests = await request_service.get_multi(pg=pagination)
    return requests


@request_router.patch("/{request_id}")
async def update_request_status(
        request_id: int,
        new_status: RequestStatus,
        current_reader: CurrentReaderType,
        request_service: RequestServiceType,
):
    if current_reader.role == Role.READER:
        raise Forbidden

    request = await request_service.update_status(request_id, new_status)
    return request


@request_router.post("/notify")
async def notify_requests(
        book_id: Annotated[int, Body(embeded=True)],
        request_service:RequestServiceType,
):
    response = await request_service.send_notify(book_id)
    return response