import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))

    # Метод для создания хэша пароля
    def create_password_hash(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    # Метод для проверки пароля
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)


class DeviceStat(Base):
    __tablename__ = "device_stats"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)



class Statistic(BaseModel):
    x: float
    y: float
    z: float
