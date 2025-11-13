from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import Base
from app.models.types import BookCopyStatus, BookAccessType


class BookCopyORM(Base):
    __tablename__ = "book_copies"

    serial_num: Mapped[str] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    status: Mapped[BookCopyStatus] = mapped_column(default=BookCopyStatus.AVAILABLE)
    access_type: Mapped[BookAccessType] = mapped_column(default=BookAccessType.TAKE_HOME)

    book: Mapped["BookORM"] = relationship(
        "BookORM",
        back_populates="copies",
    )
