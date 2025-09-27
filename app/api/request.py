from typing import Annotated, List

from fastapi import APIRouter
from fastapi.params import Depends, Query

from app.deps import Deps
from app.models.types import Role, Status
from app.schemas import RequestDTO, UserRelationDTO, RequestRelationDTO
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
) -> List[RequestRelationDTO]:
    if current_user.role == Role.employee or current_user.role == Role.admin:
        requests = await request_service.get_multi(pg=pagination)
        return requests
    else:
        raise Forbidden

@request_router.patch("/{request_id}")
async def update_request_status(
    request_id: int,
    new_status: Status,
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
):
    if current_user.role == Role.employee or current_user.role == Role.admin:
        request = await request_service.update_status(request_id, new_status)
        return request
    else:
        raise Forbidden

@request_router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)]
) -> RequestDTO:
    if current_user.role == Role.employee or current_user.role == Role.admin:
        request = await request_service.remove_request(request_id)
        return request
    else:
        raise Forbidden