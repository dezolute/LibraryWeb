from datetime import datetime, timedelta

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import Status


class RequestORM(Base):
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id', ondelete='CASCADE', onupdate='CASCADE'))
    status: Mapped[Status] = mapped_column(default=Status.accepted)
    return_by: Mapped[datetime] = mapped_column(default=(datetime.now() + timedelta(days=14)))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now())

    user: Mapped["UserORM"] = relationship(
        back_populates="requests",
    )
    book: Mapped["BookORM"] = relationship(
        backref="requests",
    )
