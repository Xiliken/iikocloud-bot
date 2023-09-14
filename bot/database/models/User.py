from sqlalchemy import Column,  String, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.Base import Base


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    is_admin: Mapped[bool] = mapped_column(default=0)
    phone_number: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __repr__(self):
        return f"User(id={self.user_id!r}, phone={self.phone_number!r} admin={self.is_admin!r})"







