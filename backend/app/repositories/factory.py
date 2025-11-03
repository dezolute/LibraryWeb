from typing import TypeVar

from app.models import ReaderORM, BookORM, BookCopyORM, LoanORM, RequestORM, ProfileORM
from app.repositories.sqlalchemy import SqlAlchemyRepository

RepositoryType = TypeVar("RepositoryType", bound=SqlAlchemyRepository)

class RepositoryFactory:

    @staticmethod
    def reader_repository() -> RepositoryType:
        return SqlAlchemyRepository(ReaderORM)

    @staticmethod
    def book_repository() -> RepositoryType:
        return SqlAlchemyRepository(BookORM)

    @staticmethod
    def book_copy_repository() -> RepositoryType:
        return SqlAlchemyRepository(BookCopyORM)

    @staticmethod
    def loan_repository() -> RepositoryType:
        return SqlAlchemyRepository(LoanORM)

    @staticmethod
    def request_repository() -> RepositoryType:
        return SqlAlchemyRepository(RequestORM)

    @staticmethod
    def profile_repository() -> RepositoryType:
        return SqlAlchemyRepository(ProfileORM)
