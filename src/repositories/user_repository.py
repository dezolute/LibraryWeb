from sqlalchemy.orm import selectinload

from src.repositories.sqlalchemy_repository import SqlAlchemyRepository
from src.models.user import UserORM


class UserRepository(SqlAlchemyRepository):
    model = UserORM
    options = [selectinload(UserORM.requests)]
