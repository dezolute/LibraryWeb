import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from datetime import datetime

from fastapi import HTTPException
from app.services.request import RequestService
from app.models.types import RequestStatus, BookCopyStatus, Role
from app.schemas.utils import Pagination


@pytest.mark.asyncio
async def test_create_request_conflict(monkeypatch):
    request_repo = AsyncMock()
    reader_service = AsyncMock()
    # reader has a request with same book id
    existing = SimpleNamespace(book=SimpleNamespace(id=1), status=RequestStatus.PENDING)
    reader = SimpleNamespace(id=1, requests=[existing])
    reader_service.get_orm_data.return_value = reader

    # bypass pydantic validation of reader in RequestService.create_request
    monkeypatch.setattr("app.services.request.ReaderRelationDTO.model_validate", lambda v: v)

    book_service = AsyncMock()

    service = RequestService(request_repository=request_repo, reader_service=reader_service, book_service=book_service)

    with pytest.raises(HTTPException) as exc:
        await service.create_request(reader_id=1, book_id=1)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_create_request_limit_exceeded(monkeypatch):
    request_repo = AsyncMock()
    reader_service = AsyncMock()
    # create 5 non-fulfilled requests
    reqs = [SimpleNamespace(status=RequestStatus.PENDING, book=SimpleNamespace(id=i)) for i in range(5)]
    reader = SimpleNamespace(id=1, requests=reqs)
    reader_service.get_orm_data.return_value = reader

    # bypass pydantic validation of reader in RequestService.create_request
    monkeypatch.setattr("app.services.request.ReaderRelationDTO.model_validate", lambda v: v)

    book_service = AsyncMock()

    service = RequestService(request_repository=request_repo, reader_service=reader_service, book_service=book_service)

    with pytest.raises(HTTPException) as exc:
        await service.create_request(reader_id=1, book_id=99)
    assert exc.value.status_code == 406


@pytest.mark.asyncio
async def test_update_status_not_found():
    request_repo = AsyncMock()
    request_repo.update.return_value = None
    service = RequestService(request_repository=request_repo, reader_service=AsyncMock(), book_service=AsyncMock())

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await service.update_status(request_id=1, new_status=RequestStatus.FULFILLED)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_send_notify_not_found():
    request_repo = AsyncMock()
    request_repo.find_all.return_value = ([], 0)
    service = RequestService(request_repository=request_repo, reader_service=AsyncMock(), book_service=AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await service.send_notify(book_id=1)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_send_notify_success(monkeypatch):
    request_repo = AsyncMock()
    # prepare a request-like dict
    req = SimpleNamespace(
        id=10,
        reader_id=2,
        book_id=3,
        status=RequestStatus.QUEUED,
        given_at=None,
        returned_at=None,
        created_at=datetime.now(),
        reader=SimpleNamespace(email="u@x.com"),
        book=SimpleNamespace(title="Book Title"),
    )
    request_repo.find_all.return_value = ([req], 1)

    # patch email sender to avoid side effects
    monkeypatch.setattr("app.modules.email.send_notification_email", AsyncMock())

    service = RequestService(request_repository=request_repo, reader_service=AsyncMock(), book_service=AsyncMock())
    result = await service.send_notify(book_id=3)
    assert result.id == 10
