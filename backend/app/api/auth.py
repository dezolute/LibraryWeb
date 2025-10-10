from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Body, Response
from fastapi.params import Cookie
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.config import oauth_config
from app.deps import Deps
from app.schemas.utils import Token
from app.services import AuthService
from app.utils import generate_google_oauth_redirect_uri

import aiohttp

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
    print(form_data.password, form_data.username)

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


# @auth_router.get("/auth/google/uri")
# async def get_google_redirect_uri():
#     url = generate_google_oauth_redirect_uri()
#     return RedirectResponse(url=url)
#
# @auth_router.post("/auth/google/callback")
# async def get_google_callback(
#     code: Annotated[str, Body(embedded=True)],
#     auth_service: Annotated[AuthService, Depends()],
# ):
#     google_token_url = "https://oauth2.googleapis.com/token"
#
#     async with aiohttp.ClientSession() as session, session.post(
#             google_token_url,
#             data={
#                 "client_id": oauth_config.OAUTH_GOOGLE_CLIENT_ID,
#                 "client_secret": oauth_config.OAUTH_GOOGLE_CLIENT_SECRET,
#                 "grant_type": "authorization_code",
#                 "redirect_uri": "http://localhost/auth/google",
#                 "code": code
#             },
#             ssl=False,
#     ) as response:
#         res = await response.json()
