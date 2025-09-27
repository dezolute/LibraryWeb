from typing import Union, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload, InstrumentedAttribute, selectinload

from src.config.database import db
from src.repositories.sqlalchemy_repository import SqlAlchemyRepository, ModelType
from src.models import RequestORM


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
    ) -> List[ModelType]:
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
            return result.unique().scalars().all()