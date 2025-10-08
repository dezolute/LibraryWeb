from typing import List

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.config.database import db
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
            total = await session.execute(func.count())
            return result.unique().scalars().all(), total.scalar()