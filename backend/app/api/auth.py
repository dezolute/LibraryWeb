from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Response
from fastapi.params import Cookie
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
    response: Response,
) -> Token:
    tokens = await auth_service.login(form_data)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        expires=7*24*3600,
        path="/"
    )
    return Token(access_token=tokens.access_token, token_type="Bearer")

@auth_router.post("/refresh")
async def refresh_tokens(
    auth_service: Annotated[AuthService, Depends(Deps.auth_service)],
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
) -> Token:
    tokens = await auth_service.refresh_tokens(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        expires=7*24*3600,
        path="/"
    )
    return Token(access_token=tokens.access_token, token_type="Bearer")