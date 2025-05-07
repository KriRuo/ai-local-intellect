from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    platform = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text)
    summary = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True))
    thumbnail = Column(String, nullable=True)
    author = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 