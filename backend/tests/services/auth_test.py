import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.auth import AuthService
from app.utils.auth.oauth2 import OAuth2Utility
from app.schemas.utils import Token


class DummyForm:
    def __init__(self, username, password):
        self.username = username
        self.password = password


@pytest.mark.asyncio
async def test_login_success(monkeypatch):
    # Мок reader
    reader = MagicMock()
    reader.email = "test@example.com"
    reader.encrypted_password = "hashed"
    reader.profile.full_name = "John Doe"

    # Мок репозиторий
    repo = AsyncMock()
    repo.find.return_value = reader

    # Мок утилиты
    monkeypatch.setattr(OAuth2Utility, "verify_password", lambda raw, hashed: True)
    monkeypatch.setattr(OAuth2Utility, "get_tokens", lambda data: Token(access_token="abc", token_type="bearer"))

    auth = AuthService(reader_repository=repo)
    form = DummyForm(username="test@example.com", password="123")

    token = await auth.login(form)
    assert token.access_token == "abc"
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(monkeypatch):
    reader = MagicMock()
    reader.email = "test@example.com"
    reader.encrypted_password = "hashed"
    reader.profile.full_name = "John Doe"

    repo = AsyncMock()
    repo.find.return_value = reader

    monkeypatch.setattr(OAuth2Utility, "verify_password", lambda raw, hashed: False)

    auth = AuthService(reader_repository=repo)
    form = DummyForm(username="test@example.com", password="wrong")

    with pytest.raises(HTTPException) as exc:
        await auth.login(form)

    assert exc.value.status_code == 401
    assert "Incorrect email or password" in exc.value.detail


@pytest.mark.asyncio
async def test_login_user_not_found():
    repo = AsyncMock()
    repo.find.return_value = None

    auth = AuthService(reader_repository=repo)
    form = DummyForm(username="notfound@example.com", password="123")

    with pytest.raises(HTTPException) as exc:
        await auth.login(form)

    assert exc.value.status_code == 401
