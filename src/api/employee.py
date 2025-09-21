from typing import Annotated, List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy.sql.functions import current_user
from starlette import status

from src.deps import Deps
from src.models.types import Role, Status
from src.schemas import UserDTO, RequestDTO
from src.schemas.utils import Pagination
from src.services.request import RequestService
from src.utils import OAuth2Utility


Forbidden = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to perform this action."
)


employee_router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
)


@employee_router.get("/requests")
async def get_requests(
    pagination: Annotated[Pagination, Query(Pagination)],
    current_user: Annotated[UserDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
) -> List[RequestDTO]:
    if current_user.role == Role.employee or current_user.role == Role.admin:
        requests = await request_service.get_multi(pg=pagination)
        return requests
    else:
        raise Forbidden

@employee_router.patch("/requests/{request_id}")
async def update_request_status(
    request_id: int,
    new_status: Status,
    current_user: Annotated[UserDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
):
    if current_user.role == Role.employee or current_user.role == Role.admin:
        request = await request_service.update_status(request_id, new_status)
        return request
    else:
        raise Forbidden

@employee_router.delete("/requests/{request_id}")
async def delete_request(
    request_id: int,
    current_user: Annotated[UserDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)]
) -> RequestDTO:
    if current_user.role == Role.employee or current_user.role == Role.admin:
        request = await request_service.remove_request(request_id)
        return request
    else:
        raise Forbidden