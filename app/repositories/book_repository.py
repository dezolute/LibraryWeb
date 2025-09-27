from .sqlalchemy_repository import SqlAlchemyRepository
from app.models.book import BookORM


class BookRepository(SqlAlchemyRepository):
    model = BookORM
