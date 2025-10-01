from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import Role


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[Role] = mapped_column(default=Role.user)
    char_id: Mapped[Optional[int]]
    icon: Mapped[Optional[str]]
    encrypted_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    requests: Mapped[Optional[list["RequestORM"]]] = relationship(
        back_populates="user",
    )