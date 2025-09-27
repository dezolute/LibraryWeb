from src.repositories import UserRepository, BookRepository, RequestRepository
from src.services import AuthService, BookService, UserService
from src.services.request import RequestService


class Deps:
    @staticmethod
    def auth_service():
        return AuthService(UserRepository)

    @staticmethod
    def user_service():
        return UserService(UserRepository)

    @staticmethod
    def book_service():
        return BookService(BookRepository)

    @staticmethod
    def request_service():
        return RequestService(RequestRepository)