from typing import TypeVar

from app.models import ReaderORM, BookORM, BookCopyORM, LoanORM, RequestORM, ProfileORM
from app.repositories.sqlalchemy import SqlAlchemyRepository

class RepositoryFactory:

    @staticmethod
    def reader_repository() -> SqlAlchemyRepository:
        return SqlAlchemyRepository[ReaderORM](ReaderORM)

    @staticmethod
    def book_repository() -> SqlAlchemyRepository:
        return SqlAlchemyRepository[BookORM](BookORM)

    @staticmethod
    def book_copy_repository() -> SqlAlchemyRepository:
        return SqlAlchemyRepository[BookCopyORM](BookCopyORM)

    @staticmethod
    def loan_repository() -> SqlAlchemyRepository:
        return SqlAlchemyRepository[LoanORM](LoanORM)

    @staticmethod
    def request_repository() -> SqlAlchemyRepository:
        return SqlAlchemyRepository[RequestORM](RequestORM)

    @staticmethod
    def profile_repository() -> SqlAlchemyRepository:
        return SqlAlchemyRepository[ProfileORM](ProfileORM)
