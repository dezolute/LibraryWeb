from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config.database import db
from src.models import RequestORM
from src.models.types import Role
from src.repositories.sqlalchemy_repository import SqlAlchemyRepository, ModelType
from src.models.user import UserORM


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

    async def create_employee(self, data: dict) -> ModelType:
        async with db.get_session() as session:
            model = self.model(**data)
            model.role = Role.admin

            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def create_admin(self, data: dict) -> ModelType:
        async with db.get_session() as session:
            model = self.model(**data)
            model.role = Role.admin

            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model