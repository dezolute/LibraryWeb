from app.models.book import BookORM
from .sqlalchemy_repository import SqlAlchemyRepository


class BookRepository(SqlAlchemyRepository):
    model = BookORM
