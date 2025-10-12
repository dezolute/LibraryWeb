from typing import List

from sqlalchemy import select, func

from app.models.book import BookORM
from .sqlalchemy_repository import SqlAlchemyRepository, ModelType
from ..config.database import db
from ..schemas.utils.filters import BookFilter


class BookRepository(SqlAlchemyRepository):
    model = BookORM

    async def find_books(
        self,
        book_filter: BookFilter,
        limit: int = 100,
        offset: int = 0,
        order_by: str = None,
    ) -> (List[ModelType], int):
        async with db.get_session() as session:
            query = (
                select(self.model)
                .limit(limit)
                .offset(offset)
                .order_by(order_by)
            )
            if book_filter.author:
                query = query.where(BookORM.author.ilike(f"%{book_filter.author}%"))
            if book_filter.publisher:
                query = query.where(BookORM.publisher.ilike(f"%{book_filter.publisher}%"))
            if book_filter.year_publication:
                query = query.where(BookORM.year_publication == book_filter.year_publication)


            result = await session.execute(query)
            total = await session.scalar(
                select(func.count()).select_from(self.model)
            )

            return result.unique().scalars().all(), total