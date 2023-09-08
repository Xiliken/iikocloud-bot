from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)


