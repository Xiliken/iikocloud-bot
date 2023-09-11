from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, Boolean

from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    is_admin = Column(Boolean, nullable=True)
    phone_number = Column(String, nullable=False, unique=True)

    def __int__(self, user_id: BigInteger, phone_number: str, is_admin: bool = False):
        self.user_id = user_id,
        self.phone_number = phone_number
        self.is_admin = is_admin






