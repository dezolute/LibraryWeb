from typing import Annotated

from fastapi import APIRouter, Depends, Body
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

@auth_router.get("/")
async def root():
    return {"message": "Hello World"}

@auth_router.post("/token")
async def create_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(Deps.auth_service)],
) -> Token:
    token = await auth_service.login(form_data)
    return token

@auth_router.get("/refresh")
async def refresh_access_token(
    refresh_token: str
):


@auth_router.get("/auth/google/uri")
async def get_google_redirect_uri():
    url = generate_google_oauth_redirect_uri()
    return RedirectResponse(url=url)

@auth_router.post("/auth/google/callback")
async def get_google_callback(
    code: Annotated[str, Body(embedded=True)],
    auth_service: Annotated[AuthService, Depends()],
):
    google_token_url = "https://oauth2.googleapis.com/token"

    async with aiohttp.ClientSession() as session, session.post(
            google_token_url,
            data={
                "client_id": oauth_config.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": oauth_config.OAUTH_GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost/auth/google",
                "code": code
            },
            ssl=False,
    ) as response:
        res = await response.json()
