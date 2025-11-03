from datetime import timedelta, date
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import Base


class LoanORM(Base):
    __tablename__ = 'loans'

    id: Mapped[int] = mapped_column(primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey('readers.id'))
    copy_id: Mapped[str] = mapped_column(ForeignKey('book_copies.serial_num'))
    issue_date: Mapped[date] = mapped_column(default=date.today())
    due_date: Mapped[date] = mapped_column(default=date.today() + timedelta(days=14))
    return_date: Mapped[Optional[date]]

    reader: Mapped["ReaderORM"] = relationship(
        back_populates="loans",
    )
    book_copy: Mapped["BookCopyORM"] = relationship(
        backref="loans",
    )
