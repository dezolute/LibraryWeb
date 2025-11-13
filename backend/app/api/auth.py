from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.deps import Deps
from app.schemas.utils import Token
from app.services import AuthService

auth_router = APIRouter(
    tags=["Auth"],
    prefix="/auth",
)


@auth_router.post("")
async def create_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: Annotated[AuthService, Depends(Deps.auth_service)],
) -> Token:
    token = await auth_service.login(form_data)
    return token
