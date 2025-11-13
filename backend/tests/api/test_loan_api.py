import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.api.loan import loan_router
from app.deps import Deps
from app.utils import OAuth2Utility
from app.models.types import Role, BookCopyStatus, BookAccessType


@pytest.fixture
def client():
    app = FastAPI()

    mock_service = AsyncMock()
    mock_reader = AsyncMock()
    mock_reader.role = Role.ADMIN
    mock_reader.id = 1

    app.dependency_overrides[Deps.loan_service] = lambda: mock_service
    app.dependency_overrides[OAuth2Utility.get_current_reader] = lambda: mock_reader

    app.include_router(loan_router)
    return TestClient(app), mock_service


@pytest.mark.asyncio
async def test_get_loans_success(client):
    client, mock_service = client

    mock_service.get_loans.return_value = {
        "id": 1,
        "reader_id": 1,
        "copy_id": 1,
        "user": {"id": 1, "email": "a@b.com", "role": Role.READER, "verified": True},
        "book_copy": {
            "serial_num": "s1",
            "status": BookCopyStatus.AVAILABLE,
            "access_type": BookAccessType.READING_ROOM,
            "book": {
                "id": 1,
                "title": "T",
                "author": "A",
                "publisher": "P",
                "year_publication": 2000,
                "copies": None,
                "cover_url": None,
            }
        }
    }

    response = client.get("/loans")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_loan_success(client):
    client, mock_service = client
    mock_service.create.return_value = {"id": 1, "reader_id": 1, "copy_id": 1}

    response = client.post("/loans", json={"reader_id": 1, "copy_id": 1})
    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_set_loan_returned_success(client):
    client, mock_service = client
    mock_service.set_loan_as_returned.return_value = {"id": 1, "reader_id": 1, "copy_id": 1}

    response = client.patch("/loans/1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_overdue_loans_success(client):
    client, mock_service = client
    mock_service.get_overdue_loans.return_value = {"items": [], "total": 0}

    response = client.get("/loans/overdue")
    assert response.status_code == 200
