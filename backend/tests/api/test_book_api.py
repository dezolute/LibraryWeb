import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.api.book import book_router
from app.deps import Deps
from app.utils import OAuth2Utility
from app.models.types import Role
from app.schemas import BookCreateDTO, BookDTO

@pytest.fixture
def client():
    app = FastAPI()

    mock_service = AsyncMock()
    mock_reader = AsyncMock()
    mock_reader.role = Role.ADMIN

    # override the underlying dependency callables (Deps.book_service and OAuth2Utility.get_current_reader)
    app.dependency_overrides[Deps.book_service] = lambda: mock_service
    app.dependency_overrides[OAuth2Utility.get_current_reader] = lambda: mock_reader

    app.include_router(book_router)
    return TestClient(app), mock_service

@pytest.mark.asyncio
async def test_create_book_success(client):
    client, mock_service = client
    mock_service.add_book.return_value = {
        "id": 1,
        "title": "New Book",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2000,
        "count": 1,
        "copies": None,
        "cover_url": None
    }

    response = client.post("/books", json={
        "title": "New Book",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2000,
        "count": 1,
        "copies": []
    })

    assert response.status_code == 200
    assert response.json()["title"] == "New Book"

@pytest.mark.asyncio
async def test_get_book_success(client):
    client, mock_service = client
    mock_service.get_single.return_value = {
        "id": 1,
        "title": "Book",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2000,
        "cover_url": None,
        "copies": []
    }

    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

@pytest.mark.asyncio
async def test_delete_book_success(client):
    client, mock_service = client
    mock_service.delete_book.return_value = {
        "id": 1,
        "title": "Deleted",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2000,
        "count": 0,
        "copies": None,
        "cover_url": None
    }

    response = client.delete("/books/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Deleted"

@pytest.fixture
def user_client():
    app = FastAPI()

    mock_service = AsyncMock()
    mock_reader = AsyncMock()
    mock_reader.role = Role.READER

    app.dependency_overrides[Deps.book_service] = lambda: mock_service
    app.dependency_overrides[OAuth2Utility.get_current_reader] = lambda: mock_reader

    app.include_router(book_router)
    return TestClient(app)

def test_create_book_forbidden(user_client):
    response = user_client.post("/books", json={
        "title": "New Book",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2000,
        "count": 1,
        "copies": []
    })

    assert response.status_code == 403
