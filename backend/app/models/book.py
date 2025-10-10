from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .types import Priority


class BookORM(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]
    priority: Mapped[Priority]
    cover: Mapped[Optional[str]]
    count: Mapped[int]
    year_publication: Mapped[int]
