from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
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

class RssScrapeRun(Base):
    __tablename__ = "rss_scrape_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    num_sources_total = Column(Integer, default=0)
    num_sources_skipped = Column(Integer, default=0)
    num_sources_captured = Column(Integer, default=0)
    num_articles_captured = Column(Integer, default=0)
    status = Column(String, default="completed")  # completed, failed, running
    error_message = Column(String, nullable=True) 