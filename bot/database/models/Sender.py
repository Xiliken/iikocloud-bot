from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models import Base


class Sender(Base):
    __tablename__ = "users_for_sender"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    status = Mapped[str] = mapped_column(unique=True, nullable=False)
    description = Mapped[str] = mapped_column(nullable=True)
