from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from .database import Base
import json

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
    tags = Column(Text, nullable=True)  # Store as JSON string
    category = Column(String, nullable=True)

    def get_tags(self) -> list:
        """Get tags as a list"""
        if self.tags:
            return json.loads(self.tags)
        return []

    def set_tags(self, tags: list):
        """Set tags from a list"""
        self.tags = json.dumps(tags) if tags else None

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
    skipped_sources_details = Column(Text, nullable=True)  # JSON: [{source, url, reason}] 