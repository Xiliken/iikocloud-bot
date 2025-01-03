from datetime import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.Base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    is_admin: Mapped[bool] = mapped_column(default=0)
    phone_number: Mapped[str] = mapped_column(nullable=False, unique=True)
    registration_date: Mapped[datetime] = mapped_column(nullable=True, default=datetime.now())
    last_order_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=True)
    reviews: Mapped[List["Review"]] = relationship()

    def __repr__(self):
        return (
            f"User(user_id={self.user_id!r}, "
            f"phone_number={self.phone_number!r}, "
            f"is_admin={self.is_admin!r},"
            f"registration_date={self.registration_date!r},"
            f"last_order_date={self.last_order_date},"
            f"is_blocked={self.is_blocked!r}) "
        )
