import pytest
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace
from fastapi import HTTPException
from app.services.book import BookService
from app.schemas import BookCreateDTO
from app.models.types import BookCopyStatus, BookAccessType

@pytest.mark.asyncio
async def test_get_single_success():
    repo = AsyncMock()
    repo.find.return_value = {
        "id": 1,
        "title": "Test Book",
        "author": "Author",
        "publisher": "Publisher",
        "year_publication": 2000,
        "cover_url": None,
        "copies": []
    }

    service = BookService(book_repository=repo, book_copy_repository=AsyncMock())
    result = await service.get_single(id=1)

    assert result.id == 1
    assert result.title == "Test Book"

@pytest.mark.asyncio
async def test_get_single_not_found():
    repo = AsyncMock()
    repo.find.return_value = None

    service = BookService(book_repository=repo, book_copy_repository=AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await service.get_single(id=999)

    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_add_book_success():
    book_dto = BookCreateDTO(
        title="New Book",
        author="Author",
        publisher="Publisher",
        year_publication=2000,
        copies=[{"serial_num": "abc123", "access_type": BookAccessType.READING_ROOM}]
    )

    book_repo = AsyncMock()
    # return object with attributes (used by service to access .id and later .copies)
    book_repo.create.return_value = SimpleNamespace(
        id=1,
        title="New Book",
        author="Author",
        publisher="Publisher",
        year_publication=2000,
        cover_url=None,
        copies=[],
    )

    copy_repo = AsyncMock()
    copy_repo.create_multiple.return_value = [SimpleNamespace(serial_num="abc123", status=BookCopyStatus.AVAILABLE, access_type=BookAccessType.READING_ROOM)]

    service = BookService(book_repository=book_repo, book_copy_repository=copy_repo)
    result = await service.add_book(book_dto)

    assert result.title == "New Book"
    assert result.copies[0].serial_num == "abc123"

@pytest.mark.asyncio
async def test_update_book_success(monkeypatch):
    book_repo = AsyncMock()
    # emulate ORM-like object with attributes for db_book
    find_results = [
        SimpleNamespace(id=1, title="Old", author="A", publisher="P", year_publication=2000, cover_url=None, copies=[]),  # первый вызов find
        SimpleNamespace(id=1, title="Updated", author="A", publisher="P", year_publication=2000, cover_url=None, copies=[])  # второй вызов find после update
    ]
    book_repo.find.side_effect = find_results
    book_repo.update.return_value = None  # update возвращает None, т.к. мы получаем обновленные данные через find

    monkeypatch.setattr("app.services.book.notify", AsyncMock())

    service = BookService(book_repository=book_repo, book_copy_repository=AsyncMock())
    dto = BookCreateDTO(title="Updated", author="A", publisher="P", year_publication=2000, copies=[])

    result = await service.update_book(book_id=1, host="localhost", book=dto)
    assert result.title == "Updated"
