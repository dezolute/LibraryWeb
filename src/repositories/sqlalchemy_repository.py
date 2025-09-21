from typing import List, TypeVar, Generic

from sqlalchemy import insert, update, delete, select
from sqlalchemy.orm import joinedload

from src.config.database import db
from src.repositories import AbstractRepository
from src.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class SqlAlchemyRepository(AbstractRepository, Generic[ModelType]):
    model = None
    options = []

    async def create(self, data: dict) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                insert(self.model)
                .values(**data)
                .options(*self.options)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().one()

    async def create_multiple(self, data: List[dict]) -> List[ModelType]:
        async with db.get_session() as session:
            list_models = []
            for row in data:
                model = self.model(**row)
                list_models.append(model)

            session.add_all(list_models).options(*self.options)
            await session.commit()
            return list_models

    async def update(self, data: dict, **filters) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                update(self.model)
                .values(**data)
                .filter_by(**filters)
                .options(*self.options)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalars().one()

    async def delete(self, **filters) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                delete(self.model)
                .filter_by(**filters)
                .options(*self.options)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalars().one()

    async def find(self, **filters) -> ModelType:
        async with db.get_session() as session:
            query = (
                select(self.model)
                .options(*self.options)
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.scalars().one()

    async def find_all(
        self, limit: int = 100, offset: int = 0, order_by: str = None, **filters
    ) -> List[ModelType]:
        async with db.get_session() as session:
            query = (
                select(self.model)
                .options(*self.options)
                .limit(limit)
                .offset(offset)
                .order_by(order_by)
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.unique().scalars().all()
