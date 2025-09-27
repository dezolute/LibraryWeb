from typing import Annotated

from fastapi import APIRouter, Depends

from src.utils.errors import Forbidden
from src.deps import Deps
from src.models.types import Role
from src.schemas import UserCreateDTO, UserRelationDTO
from src.services import UserService
from src.utils import OAuth2Utility

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
    if current_user.role == Role.admin:
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
    if current_user.role == Role.admin:
        db_employee = await user_service.add_employee(employee)
        return db_employee
    else:
        raise Forbidden