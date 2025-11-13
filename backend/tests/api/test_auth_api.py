import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock

from app.api.auth import auth_router
from app.schemas.utils import Token
from app.deps import Deps

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(auth_router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_access_token_success(monkeypatch, client):
    mock_auth_service = AsyncMock()
    mock_auth_service.login.return_value = Token(access_token="abc123", token_type="bearer")

    # override dependency on the app instance used by the TestClient
    # TestClient exposes the app as `.app`
    client.app.dependency_overrides[Deps.auth_service] = lambda: mock_auth_service

    response = client.post(
        "/auth",
        data={"username": "test@example.com", "password": "securepass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "abc123"
    assert response.json()["token_type"] == "bearer"
