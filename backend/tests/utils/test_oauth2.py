import pytest
import jwt
from datetime import timedelta

from app.models import ReaderORM
from app.repositories import RepositoryFactory as RF
from app.utils import OAuth2Utility
from app.config import auth_config


@pytest.mark.asyncio
async def test_get_hashed_password():
    hashed = OAuth2Utility.get_hashed_password("")
    assert hashed is not None


@pytest.mark.asyncio
async def test_verify_password():
    hashed = OAuth2Utility.get_hashed_password("123")
    assert OAuth2Utility.verify_password("123", hashed)


@pytest.mark.asyncio
async def test_create_access_token():
    data = {
        "sub": "123@example.com",
    }
    token = OAuth2Utility.create_token(data, expires_delta=timedelta(minutes=15))
    payload = jwt.decode(token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALGORITHM])
    assert payload["sub"] == "123@example.com"


@pytest.mark.asyncio
async def get_current_reader():
    reader_repo = RF.reader_repository()
    data = {
        "email": "dezo@example.com",
        "encrypted_password": "123",
        "verified": True
    }
    db_reader: ReaderORM = await reader_repo.create(data)

    try:
        token_data = {
            "sub": db_reader.email,
        }
        token = OAuth2Utility.create_token(token_data, expires_delta=timedelta(minutes=15))
        reader_dto = await OAuth2Utility.get_current_reader(token)
        assert reader_dto is not None
        assert reader_dto.id == db_reader.id
    finally:
        await reader_repo.delete(id=db_reader.id)