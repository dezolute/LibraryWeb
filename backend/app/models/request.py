from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import Status


class RequestORM(Base):
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))
    status: Mapped[Status] = mapped_column(default=Status.ACCEPTED)
    given_at: Mapped[Optional[datetime]]
    returned_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["UserORM"] = relationship(
        back_populates="requests",
    )
    book: Mapped["BookORM"] = relationship(
        backref="requests",
    )
