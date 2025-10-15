from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import Deps
from app.models.types import Role
from app.schemas import UserCreateDTO, UserRelationDTO
from app.services import UserService
from app.utils import OAuth2Utility
from app.utils.errors import Forbidden

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@admin_router.post("")
async def add_admin(
        admin: UserCreateDTO,
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
        user_service: Annotated[UserService, Depends(Deps.user_service)]
):
    if current_user.role == Role.ADMIN:
        db_admin = await user_service.add_admin(admin)
        return db_admin
    else:
        raise Forbidden


@admin_router.post("/employee")
async def add_employee(
        employee: UserCreateDTO,
        current_user: Annotated[UserRelationDTO, Depends(OAuth2Utility.get_current_user)],
        user_service: Annotated[UserService, Depends(Deps.user_service)]
):
    if current_user.role == Role.ADMIN:
        db_employee = await user_service.add_employee(employee)
        return db_employee
    else:
        raise Forbidden
