from datetime import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import RequestStatus
from .base import Base


class RequestORM(Base):
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey('readers.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))
    status: Mapped[RequestStatus] = mapped_column(default=RequestStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    reader: Mapped["ReaderORM"] = relationship(
        back_populates="requests",
    )
    book: Mapped["BookORM"] = relationship(
        back_populates="requests",
    )
