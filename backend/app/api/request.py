from typing import Annotated, List

from fastapi import APIRouter
from fastapi.params import Depends, Query, Body

from app.deps import Deps
from app.models.types import Role, Status
from app.schemas import RequestDTO, UserRelationDTO, MultiRequestDTO, RequestRelationDTO
from app.schemas.utils import Pagination
from app.services.request import RequestService
from app.utils import OAuth2Utility
from app.utils.errors import Forbidden

request_router = APIRouter(
    prefix="/requests",
    tags=["Requests"]
)


@request_router.get("")
async def get_requests(
    pagination: Annotated[Pagination, Query()],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
) -> MultiRequestDTO:
    if current_user.role == Role.USER:
        raise Forbidden

    requests = await request_service.get_multi(pg=pagination)
    return requests

@request_router.patch("/{request_id}")
async def update_request_status(
    request_id: int,
    new_status: Status,
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
):
    if current_user.role == Role.USER:
        raise Forbidden

    request = await request_service.update_status(request_id, new_status)
    return request

@request_router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)]
) -> RequestDTO:
    if current_user.role == Role.USER:
        raise Forbidden

    request = await request_service.remove_request(request_id)
    return request

@request_router.post("/notify")
async def notify_requests(
    book_id: Annotated[int, Body(embeded=True)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
):
    response = await request_service.send_notify(book_id)
    return response

@request_router.get("/overdue")
async def get_overdue_requests(
    pg: Annotated[Pagination, Query()],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)]
) -> List[RequestRelationDTO]:
    if current_user.role == Role.USER:
        return Forbidden
    requests = await request_service.get_overdue_requests(pg)
    return requests