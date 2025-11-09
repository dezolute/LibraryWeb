from app.repositories import RepositoryFactory as RF
from app.services import AuthService, BookService, ReaderService
from app.services.loan import LoanService
from app.services.request import RequestService


class Deps:
    @staticmethod
    def auth_service() -> AuthService:
        return AuthService(RF.reader_repository())

    @staticmethod
    def reader_service() -> ReaderService:
        return ReaderService(
            RF.reader_repository(),
            RF.profile_repository()
        )

    @staticmethod
    def book_service() -> BookService:
        return BookService(
            RF.book_repository(),
            RF.book_copy_repository()
        )

    @staticmethod
    def request_service() -> RequestService:
        return RequestService(
            RF.request_repository(),
            reader_service=Deps.reader_service(),
            book_service=Deps.book_service(),
            loan_service=Deps.loan_service()
        )

    @staticmethod
    def loan_service() -> LoanService:
        return LoanService(
            RF.loan_repository(),
            book_service=Deps.book_service(),
            reader_service=Deps.reader_service(),
        )
