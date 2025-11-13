from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import Role


class ReaderORM(Base):
    __tablename__ = "readers"

    repr_cols = ['verified']

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[Role] = mapped_column(default=Role.READER)
    encrypted_password: Mapped[str]
    verified: Mapped[bool] = mapped_column(default=False)

    requests: Mapped[Optional[list["RequestORM"]]] = relationship(
        "RequestORM",
        back_populates="reader",
    )
    profile: Mapped["ProfileORM"] = relationship(
        "ProfileORM",
        back_populates="reader",
        uselist=False,
        cascade="all, delete, delete-orphan",
    )
    loans: Mapped[Optional[list["LoanORM"]]] = relationship(
        "LoanORM",
        back_populates="reader",
    )
