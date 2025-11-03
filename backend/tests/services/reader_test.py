import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile, HTTPException
from pydantic import EmailStr

from app.services.reader import ReaderService
from app.schemas import ReaderCreateDTO
from app.models.types import Role

@pytest.mark.asyncio
async def test_add_reader_success(monkeypatch):
    reader_dto = ReaderCreateDTO(
        full_name="Иванов Иван Иванович",
        email="test@example.com",
        password="securepass123",
        confirm_password="securepass123"
    )

    reader_repo = AsyncMock()
    reader_repo.create.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=Role.READER,
        verified=False,
        profile=MagicMock(
            full_name="Иванов Иван Иванович",
            avatar_url=None
        )
    )

    profile_repo = AsyncMock()
    profile_repo.create.return_value = MagicMock(full_name="Иванов Иван Иванович", avatar_url=None)

    monkeypatch.setattr("app.services.reader.OAuth2Utility.get_hashed_password", lambda pwd: "hashed")
    monkeypatch.setattr("app.services.reader.send_verify_email", AsyncMock())
    monkeypatch.setattr("app.services.reader.RedisRepository.set_verify_tokens", AsyncMock())

    service = ReaderService(reader_repo, profile_repo)
    result = await service.add_reader(reader_dto)

    assert result.email == "test@example.com"
    assert result.profile.full_name == "Иванов Иван Иванович"


@pytest.mark.asyncio
async def test_set_icon_to_reader(monkeypatch, tmp_path):
    dummy_file = tmp_path / "icon.png"
    dummy_file.write_bytes(b"image")

    file = MagicMock(spec=UploadFile)
    file.filename = "icon.png"
    file.read = AsyncMock(return_value=b"image")

    monkeypatch.setattr("app.services.reader.upload_file_to_s3", lambda path: "https://s3.com/icon.png")

    profile_repo = AsyncMock()
    reader_repo = AsyncMock()
    reader_repo.find.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=Role.READER,
        verified=True,
        profile=MagicMock(
            full_name="Иванов Иван Иванович",
            avatar_url="https://s3.com/icon.png"
        )
    )

    service = ReaderService(reader_repo, profile_repo)
    result = await service.set_icon_to_reader(reader_id=1, file=file)

    assert result.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_orm_data_found():
    repo = AsyncMock()
    repo.find.return_value = MagicMock(id=1, email="test@example.com")

    service = ReaderService(reader_repository=repo, profile_repository=AsyncMock())
    result = await service.get_orm_data(id=1)

    assert result.id == 1

@pytest.mark.asyncio
async def test_get_orm_data_not_found():
    repo = AsyncMock()
    repo.find.return_value = None

    service = ReaderService(reader_repository=repo, profile_repository=AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await service.get_orm_data(id=999)

    assert exc.value.status_code == 404
