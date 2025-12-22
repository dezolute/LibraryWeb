from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import Base


class ProfileORM(Base):
    __tablename__ = 'profiles'

    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id", ondelete="CASCADE"), primary_key=True)
    avatar_url: Mapped[Optional[str]]
    full_name: Mapped[str]

    reader: Mapped["ReaderORM"] = relationship( # type: ignore
        "ReaderORM",
        back_populates="profile",
        uselist=False,
    )
