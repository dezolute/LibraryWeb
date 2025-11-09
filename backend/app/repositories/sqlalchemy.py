from typing import List, Type, Tuple, TypeVar

from sqlalchemy import update, delete, select, func, ClauseElement

from app.config.database import db
from app.models import Base
from app.repositories import AbstractRepository
from app.schemas.utils import Pagination


ModelType = TypeVar('ModelType', bound=Base)


class SqlAlchemyRepository[ModelType](AbstractRepository):
    def __init__(self, model: Type[ModelType]):
        self.model: Type[ModelType] = model

    async def create(self, data: dict) -> ModelType:
        async with db.get_session() as session:
            model = self.model(**data)
            session.add(model)
            await session.commit()
            await session.refresh(model)

            return model

    async def create_multiple(self, data: List[dict]) -> List[ModelType]:
        async with db.get_session() as session:
            list_models: list[ModelType] = []
            for row in data:
                model = self.model(**row)
                list_models.append(model)

            session.add_all(list_models)
            await session.commit()

            pk = self.model.__mapper__.primary_key[0]
            ids = [getattr(obj, pk.key) for obj in list_models]
            query = (
                select(self.model)
                .where(pk.in_(ids))
                .options(*self.model.get_loads())
            )

            result = await session.execute(query)

            return result.scalars().unique().all()

    async def update(
            self,
            data: dict,
            conditions: List[ClauseElement] = None,
            **filters
    ) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                update(self.model)
                .where(*(conditions or []))
                .values(**data)
                .filter_by(**filters)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def delete(self,
        conditions: List[ClauseElement] = None,
        **filters
    ) -> ModelType:
        async with db.get_session() as session:
            stmt = (
                delete(self.model)
                .where(*(conditions or []))
                .filter_by(**filters)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def find(
            self,
            conditions: List[ClauseElement] = None,
            **filters
    ) -> ModelType:
        async with db.get_session() as session:
            query = (
                select(self.model)
                .where(*(conditions or []))
                .options(*self.model.get_loads())
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.scalars().first()

    async def find_all(
            self,
            pg: Pagination = None,
            conditions: List[ClauseElement] = None,
            **filters,
    ) -> Tuple[List[ModelType], int]:
        async with db.get_session() as session:
            if pg is None:
                pg = Pagination()

            query = (
                select(self.model)
                .where(*(conditions or []))
                .limit(pg.limit)
                .offset(pg.offset)
                .order_by(pg.order_by)
                .options(*self.model.get_loads())
                .filter_by(**filters)
            )

            count_query = select(func.count()).select_from(
                select(self.model).where(*(conditions or [])).filter_by(**filters).subquery()
            )

            result = await session.execute(query)
            total = await session.execute(count_query)

            return result.unique().scalars().all(), total.scalar()
