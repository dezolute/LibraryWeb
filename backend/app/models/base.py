from typing import List

from sqlalchemy.orm import DeclarativeBase, selectinload, joinedload
from sqlalchemy.orm.interfaces import LoaderOption


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
    def get_loads(cls) -> List[LoaderOption]:
        loads: List[LoaderOption] = []
        for rel in cls.__mapper__.relationships:
            attr = getattr(cls, rel.key)
            if rel.uselist:
                loads.append(selectinload(attr))
            else:
                loads.append(joinedload(attr))

        return loads
