from sqlalchemy.orm import joinedload

from src.repositories.sqlalchemy_repository import SqlAlchemyRepository
from src.models import RequestORM


class RequestRepository(SqlAlchemyRepository):
    model = RequestORM
    options = [joinedload(RequestORM.user), joinedload(RequestORM.book)]