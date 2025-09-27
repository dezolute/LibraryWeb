from typing import Annotated, List

from fastapi import APIRouter
from fastapi.params import Depends, Query

from src.utils.errors import Forbidden
from src.deps import Deps
from src.models.types import Role, Status
from src.schemas import RequestDTO, UserRelationDTO, RequestRelationDTO
from src.schemas.utils import Pagination
from src.services.request import RequestService
from src.utils import OAuth2Utility


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