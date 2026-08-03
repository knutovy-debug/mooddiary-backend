from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Entry(Base):
    __tablename__ = "entries"   # <--- две подчёркивания с каждой стороны
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    sentiment = Column(String(20))
    stress_level = Column(Integer)
    topics = Column(String)
    recommendation = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())