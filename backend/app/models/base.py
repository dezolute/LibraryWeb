from typing import List, Set, Type, TypeVar

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

ModelType = TypeVar('ModelType')

class Base(DeclarativeBase):
    __abstract__ = True

    repr_cols_num = 10
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {", ".join(cols)}>"

    @classmethod
    def get_loads(cls: Type[ModelType], visited: Set[Type] = None) -> List[LoaderOption]:
        if visited is None:
            visited = set()

        if cls in visited:
            return []

        visited.add(cls)

        loads = []
        mapper = inspect(cls)

        for rel in mapper.relationships:
            attr = getattr(cls, rel.key)

            nested_loads = rel.mapper.class_.get_loads(visited)
            if nested_loads:
                loads.append(selectinload(attr).options(*nested_loads))
            else:
                loads.append(selectinload(attr))

        return loads
