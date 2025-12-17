from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BookORM(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]
    publisher: Mapped[str]
    cover_url: Mapped[Optional[str]]
    year_publication: Mapped[int]

    copies: Mapped[list["BookCopyORM"]] = relationship( # type: ignore
        "BookCopyORM",
        back_populates="book",
        cascade="all, delete, delete-orphan",
    )

    requests: Mapped[Optional[list["RequestORM"]]] = relationship( # type: ignore
        "RequestORM",
        back_populates="book"
    )
