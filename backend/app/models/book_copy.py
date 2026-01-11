from datetime import date
from typing import Optional
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import Base
from app.models.types import BookCopyStatus, BookAccessType


class BookCopyORM(Base):
    __tablename__ = "book_copies"

    serial_num: Mapped[str] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    status: Mapped[BookCopyStatus] = mapped_column(default=BookCopyStatus.AVAILABLE)
    access_type: Mapped[BookAccessType] = mapped_column(default=BookAccessType.TAKE_HOME)

    book: Mapped["BookORM"] = relationship( # type: ignore
        "BookORM",
        back_populates="copies",
    )

    histories: Mapped[list["HistoryORM"]] = relationship(
        "HistoryORM",
        back_populates="copy",
    )

class HistoryORM(Base):
    __tablename__ = "histories"

    id: Mapped[int] = mapped_column(primary_key=True)
    copy_id: Mapped[str] = mapped_column(ForeignKey("book_copies.serial_num"))
    name: Mapped[str]
    borrowed_at: Mapped[date] = mapped_column(server_default=func.now())
    borrowed_to: Mapped[Optional[date]]

    copy: Mapped[BookCopyORM] = relationship(
        "BookCopyORM",
        back_populates="histories"
    )