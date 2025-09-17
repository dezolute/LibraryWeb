from sqlalchemy import insert, update, delete, select

from src.database.db import db
from base_repository import BaseRepository



class SqlAlchemyRepository(BaseRepository):
    model = None

    async def create(self, data: dict):
        async with db.get_session() as session:
            stmt = (
                insert(self.model)
                .values(**data)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def update(self, data: dict, **filters):
        async with db.get_session() as session:
            stmt = (
                update(self.model)
                .values(**data)
                .filter_by(**filters)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one()

    async def delete(self, **filters):
        async with db.get_session() as session:
            stmt = (
                delete(self.model)
                .filter_by(**filters)
                .returning(self.model)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one()

    async def find(self, **filters):
        async with db.get_session() as session:
            query = (
                select(self.model)
                .filter_by(**filters)
            )

            result = await session.execute(query)
            return result.scalars().first()

    async def find_all(self, limit: int = 100, offset: int = 0, order: str = id, **filters):
        async with db.get_session() as session:
            query = (
                select(self.model)
                .filter_by(**filters)
                .limit(limit)
                .offset(offset)
                .order_by(order)
            )

            result = await session.execute(query)
            return result.scalars().all()