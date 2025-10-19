from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile
from starlette import status
from starlette.responses import RedirectResponse

from app.deps import Deps
from app.schemas import UserCreateDTO, RequestDTO
from app.schemas import UserDTO, UserRelationDTO, MultiRequestDTO
from app.schemas.utils import Pagination
from app.services import UserService
from app.services.request import RequestService
from app.utils import OAuth2Utility

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("")
async def create_user(
        user: UserCreateDTO,
        user_service: Annotated[UserService, Depends(Deps.user_service)],
) -> UserDTO:
    db_user = await user_service.add_user(user)
    return db_user


@user_router.get("/me")
async def get_current_user(
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
) -> UserRelationDTO:
    return current_user


@user_router.patch("/me/icon")
async def set_user_avatar(
        icon: UploadFile,
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
        user_service: Annotated[UserService, Depends(Deps.user_service)],
):
    updated_user = await user_service.set_icon_to_user(current_user.id, icon)
    return updated_user


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
) -> MultiRequestDTO:
    db_requests = await request_service.get_multi(
        pg=page,
        user_id=current_user.id,
    )
    return db_requests


@user_router.delete("/me/requests/{request_id}")
async def remove_request(
        request_id: int,
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
        request_service: Annotated[RequestService, Depends(Deps.request_service)],
) -> RequestDTO:
    request = await request_service.user_remove_request(request_id, current_user.id)
    return request

@user_router.get("/me/requests/overdue")
async def get_overdue_requests(
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
        request_service: Annotated[RequestService, Depends(Deps.request_service)],
):
    db_requests = await request_service.get_overdue_requests(
        pg=Pagination(),
        user_id=current_user.id,
    )
    return db_requests

@user_router.get("/verify")
async def get_user_verification(
        token: Annotated[str, Query()],
        user_service: Annotated[UserService, Depends(Deps.user_service)],
):
    await user_service.set_verify_email_to_user(token)
    return RedirectResponse(
        "http://localhost/login",
        status_code=status.HTTP_302_FOUND
    )
