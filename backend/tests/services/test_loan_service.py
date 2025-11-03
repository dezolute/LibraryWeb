import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from datetime import date

from app.services.loan import LoanService
from app.models.types import BookCopyStatus
from app.schemas.utils import Pagination
from app.models.types import BookAccessType
from app.models.types import RequestStatus
from app.models.types import Role


@pytest.mark.asyncio
async def test_get_loans_success():
    loan_repo = AsyncMock()
    loan_data = {
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
    loan_repo.find_all.return_value = ([loan_data], 1)

    service = LoanService(
        loan_repository=loan_repo,
        book_service=AsyncMock(),
        reader_service=AsyncMock(),
        request_service=AsyncMock(),
    )

    result = await service.get_loans(pg=Pagination(limit=100, offset=0, order_by="id"))
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].id == 1


@pytest.mark.asyncio
async def test_create_loan_success():
    loan_repo = AsyncMock()
    # db_loan must carry fields used by LoanRelationDTO
    db_loan = SimpleNamespace(
        id=1,
        reader_id=1,
        copy_id=1,
        user={"id": 1, "email": "a@b.com", "role": Role.READER, "verified": True},
        book_copy={"serial_num": "s1", "status": BookCopyStatus.BORROWED, "access_type": BookAccessType.READING_ROOM, "book": {"id": 10, "title": "T", "author": "A", "publisher": "P", "year_publication": 2000, "copies": None, "cover_url": None}},
    )
    loan_repo.create.return_value = db_loan

    # book_service returns a copy-like object
    copy_obj = SimpleNamespace(serial_num="s1", book_id=10)
    book_service = AsyncMock()
    book_service.change_copy_status.return_value = copy_obj

    # request_service returns a list-like collection; code expects indexable
    req1 = SimpleNamespace(id=5)
    request_service = AsyncMock()
    request_service.get_multi.return_value = [req1]
    request_service.update_status = AsyncMock()

    service = LoanService(
        loan_repository=loan_repo,
        book_service=book_service,
        reader_service=AsyncMock(),
        request_service=request_service,
    )

    # create a lightweight loan DTO-like object with required attrs
    loan_obj = SimpleNamespace(model_dump=lambda: {"reader_id": 1, "copy_id": 1}, serial_num="s1")

    result = await service.create_loan(loan_obj)
    assert result.id == 1
    # ensure book_service.change_copy_status was called
    book_service.change_copy_status.assert_called()
    request_service.update_status.assert_called_once()


@pytest.mark.asyncio
async def test_set_loan_as_returned_success():
    loan_repo = AsyncMock()
    # emulate loan returned by find
    loan_db = SimpleNamespace(
        id=2,
        reader_id=42,
        copy_id=7,
        user={"id": 42, "email": "u@x.com", "role": Role.READER, "verified": True},
        copy=SimpleNamespace(serial_num="s1", status=BookCopyStatus.BORROWED, access_type=BookAccessType.READING_ROOM, book={"id": 99, "title": "T", "author": "A", "publisher": "P", "year_publication": 2000, "copies": None, "cover_url": None}),
            book_copy=SimpleNamespace(serial_num="s1", status=BookCopyStatus.BORROWED, access_type=BookAccessType.READING_ROOM, book={"id": 99, "title": "T", "author": "A", "publisher": "P", "year_publication": 2000, "copies": None, "cover_url": None}),
    )
    loan_repo.update.return_value = None
    loan_repo.find.return_value = loan_db

    book_service = AsyncMock()
    book_service.change_copy_status.return_value = SimpleNamespace(serial_num="s1", status=BookCopyStatus.AVAILABLE)

    service = LoanService(
        loan_repository=loan_repo,
        book_service=book_service,
        reader_service=AsyncMock(),
        request_service=AsyncMock(),
    )

    result = await service.set_loan_as_returned(loan_id=2)
    assert result.id == 2
    book_service.change_copy_status.assert_called()


@pytest.mark.asyncio
async def test_get_overdue_loans_success():
    loan_repo = AsyncMock()
    loan_data = {
        "id": 3,
        "reader_id": 2,
        "copy_id": 2,
        "user": {"id": 2, "email": "u@x.com", "role": Role.READER, "verified": True},
        "book_copy": {"serial_num": "s2", "status": BookCopyStatus.AVAILABLE, "access_type": BookAccessType.TAKE_HOME, "book": {"id": 2, "title": "B", "author": "A", "publisher": "P", "year_publication": 2000, "copies": None, "cover_url": None}},
    }
    loan_repo.find_all.return_value = ([loan_data], 1)

    service = LoanService(
        loan_repository=loan_repo,
        book_service=AsyncMock(),
        reader_service=AsyncMock(),
        request_service=AsyncMock(),
    )

    result = await service.get_overdue_loans(pg=Pagination(limit=100, offset=0, order_by="id"))
    assert len(result.items) == 1
