from typing import List, TypeVar, Generic, Union, Optional

from sqlalchemy import update, delete, select
from sqlalchemy.orm import InstrumentedAttribute

from app.config.database import db
from app.repositories import AbstractRepository
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class SqlAlchemyRepository(AbstractRepository, Generic[ModelType]):
    model = None
    options = None

    async def create(self, data: dict) -> ModelType:
        async with db.get_session() as session:
            model = self.model(**data)

            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def create_multiple(self, data: List[dict]) -> List[ModelType]:
        async with db.get_session() as session:
            list_models = []
            for row in data:
                model = self.model(**row)
                list_models.append(model)

            session.add_all(list_models)
            await session.commit()
            return list_models

    async def update(self, data: dict, **filters) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                update(self.model)
                .values(**data)
                .filter_by(**filters)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def delete(self,
                     options: Optional[List[Union[str, InstrumentedAttribute]]] = None,
                     **filters) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                delete(self.model)
                .filter_by(**filters)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def find(self,
                   **filters) -> ModelType:
        async with db.get_session() as session:
            query = (
                select(self.model)
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
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.unique().scalars().all()

    async def create_employee(self, data: dict) -> ModelType:
        pass

    async def create_admin(self, data: dict) -> ModelType:
        pass