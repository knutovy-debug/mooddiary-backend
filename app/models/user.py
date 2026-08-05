from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_subscribed = Column(Boolean, default=False)          # <--- исправлено
    subscription_expires = Column(DateTime, nullable=True)
    telegram_id = Column(Integer, unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())