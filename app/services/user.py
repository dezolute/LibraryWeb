from typing import Callable

from app.repositories import AbstractRepository
from app.schemas import UserDTO, UserCreateDTO


class UserService:
    def __init__(self, user_repository: Callable[[], AbstractRepository]):
        self.user_repository: AbstractRepository = user_repository()

    async def add_employee(self, employee: UserCreateDTO):
        employee_dict = employee.model_dump()
        db_employee = await self.user_repository.create_employee(employee_dict)

        return UserDTO.model(db_employee)

    async def add_admin(self, admin: UserCreateDTO):
        admin_dict = admin.model_dump()
        db_admin = await self.user_repository.create_employee(admin_dict)

        return UserDTO.model_validate(db_admin)