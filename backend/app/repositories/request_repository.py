from datetime import datetime
from typing import List

from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.config.database import db
from app.models.types import Status
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository, ModelType
from app.models import RequestORM


class RequestRepository(SqlAlchemyRepository):
    model = RequestORM

    async def find(self,
                   **filters) -> ModelType:
        async with db.get_session() as session:
            query = (
                select(self.model)
                .options(joinedload(self.model.user), joinedload(self.model.book))
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.scalars().one()

    async def find_all(
        self, limit: int = 100, offset: int = 0, order_by: str = None, **filters,
    ) -> (List[ModelType], int):
        async with db.get_session() as session:
            query = (
                select(self.model)
                .limit(limit)
                .offset(offset)
                .order_by(order_by)
                .options(joinedload(self.model.user), joinedload(self.model.book))
                .filter_by(**filters)
            )

            result = await session.execute(query)
            total = await session.scalar(
                select(func.count()).select_from(self.model)
            )

            return result.unique().scalars().all(), total

    async def find_overdue(
        self, limit: int = 100, offset: int = 0, order_by: str = None,
    ) -> (List[ModelType], int):
        async with db.get_session() as session:
            query = ()
        async with db.get_session() as session:
            query = (
                select(self.model)
                .limit(100)
                .offset(0)
                .where(
                    and_(
                        self.model.status == Status.GIVEN,
                        self.model.return_by < datetime.now(),
                    )
                )
            )

            result = await session.execute(query)
            total = await session.scalar(
                select(func.count()).select_from(self.model)
            )

            return result.unique().scalars().all(), total