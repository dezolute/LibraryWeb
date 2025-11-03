import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from datetime import datetime

from app.api.request import request_router
from app.deps import Deps
from app.utils import OAuth2Utility
from app.models.types import Role, RequestStatus


@pytest.fixture
def client():
    app = FastAPI()

    mock_service = AsyncMock()
    mock_reader = AsyncMock()
    mock_reader.role = Role.ADMIN
    mock_reader.id = 1

    app.dependency_overrides[Deps.request_service] = lambda: mock_service
    app.dependency_overrides[OAuth2Utility.get_current_reader] = lambda: mock_reader

    app.include_router(request_router)
    return TestClient(app), mock_service


@pytest.mark.asyncio
async def test_get_requests_success(client):
    client, mock_service = client

    mock_service.get_multi.return_value = {"items": [], "total": 0}

    response = client.get("/requests")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_request_status_success(client):
    client, mock_service = client
    mock_service.update_status.return_value = {
        "id": 1,
        "reader_id": 1,
        "book_id": 1,
        "status": RequestStatus.PENDING,
        "given_at": None,
        "returned_at": None,
        "created_at": datetime.utcnow().isoformat(),
    }

    # pass enum value as query param
    response = client.patch("/requests/1", params={"new_status": RequestStatus.PENDING.value})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_notify_requests_success(client):
    client, mock_service = client
    mock_service.send_notify.return_value = {"ok": True}

    # the endpoint expects a raw int body (book id)
    response = client.post("/requests/notify", json=1)
    assert response.status_code == 200
    assert response.json()["ok"] is True
