from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime
from sqlalchemy.orm import Mapped

from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[BigInteger] = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)



