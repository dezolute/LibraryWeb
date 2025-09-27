from .sqlalchemy_repository import SqlAlchemyRepository
from src.models.book import BookORM


class BookRepository(SqlAlchemyRepository):
    model = BookORM
