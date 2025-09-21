from typing import Callable

from src.repositories import AbstractRepository
from src.schemas import UserDTO, UserCreateDTO


class UserService:
    def __init__(self, user_repository: Callable[[], AbstractRepository]):
        self.user_repository: AbstractRepository = user_repository()
