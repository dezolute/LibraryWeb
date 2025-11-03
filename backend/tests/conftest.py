from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config.database import db
from app.models import Base
from app.repositories import RepositoryFactory

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DB_URL, echo=False)
SessionTest = async_sessionmaker(engine, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope="session")
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionTest() as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
async def setup_dependency_overrides(override_get_session):
    db.get_session = lambda: override_get_session

@pytest.fixture()
def book_repo():
    return RepositoryFactory.book_repository()