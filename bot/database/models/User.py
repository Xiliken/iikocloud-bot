from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.Base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        primary_key=True, unique=True, autoincrement=False
    )
    is_admin: Mapped[bool] = mapped_column(default=0)
    phone_number: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __repr__(self):
        return f"User(user_id={self.user_id!r}, phone_number={self.phone_number!r} is_admin={self.is_admin!r})"
