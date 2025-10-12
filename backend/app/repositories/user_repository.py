from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config.database import db
from app.models import RequestORM
from app.models.types import Role
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository, ModelType
from app.models.user import UserORM


class UserRepository(SqlAlchemyRepository):
    model = UserORM

    async def find(self,
                   **filters) -> ModelType:
        async with db.get_session() as session:
            query = (
                select(self.model)
                .options(
                    selectinload(self.model.requests)
                    .joinedload(RequestORM.book)
                )
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.scalars().first()

    async def find_all(
        self, limit: int = 100, offset: int = 0, order_by: str = None, **filters,
    ) -> List[ModelType]:
        async with db.get_session() as session:
            query = (
                select(self.model)
                .limit(limit)
                .offset(offset)
                .order_by(order_by)
                .options(
                    selectinload(self.model.requests)
                    .joinedload(RequestORM.book)
                )
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.unique().scalars().all()