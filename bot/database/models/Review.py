import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    review_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), nullable=False)
    food_rating: Mapped[int] = mapped_column(default=0, nullable=True)
    service_rating: Mapped[int] = mapped_column(default=0, nullable=True)
