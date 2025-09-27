from typing import Annotated, List

from fastapi import APIRouter, Depends, Query

from app.deps import Deps
from app.schemas import UserCreateDTO, RequestDTO
from app.schemas import UserDTO
from app.schemas.user import UserRelationDTO, RequestRelationDTO
from app.schemas.utils import Pagination
from app.services import AuthService
from app.services.request import RequestService
from app.utils import OAuth2Utility

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("")
async def create_user(
    user_service: Annotated[AuthService, Depends(Deps.auth_service)],
    user: UserCreateDTO,
) -> UserDTO:
    db_user = await user_service.add_user(user)
    return db_user


@user_router.get("/me")
async def get_current_user(
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> UserRelationDTO:
    return current_user

@user_router.post("/me/requests")
async def make_requests(
    book_id: int,
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
) -> RequestDTO:
    requests = await request_service.create_request(
        user_id=current_user.id,
        book_id=book_id,
    )
    return requests

@user_router.get("/me/requests")
async def get_user_requests(
    page: Annotated[Pagination, Query()],
    current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
    request_service: Annotated[RequestService, Depends(Deps.request_service)],
) -> List[RequestRelationDTO]:
    requests = await request_service.get_multi(
        pg=page,
        user_id=current_user.id,
    )
    return requests

@user_router.delete("/me/requests/{request_id}")
async def remove_request(
        request_id: int,
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
        request_service: Annotated[RequestService,  Depends(Deps.request_service)],
) -> RequestDTO:
    request = await request_service.user_remove_request(request_id, current_user.id)

    return request
