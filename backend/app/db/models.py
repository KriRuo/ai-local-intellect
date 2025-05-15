from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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
    tag_status = Column(String, default="pending")  # pending, tagged, error

    def get_tags(self) -> list:
        """Get tags as a list"""
        if self.tags:
            return json.loads(self.tags)
        return []

    def set_tags(self, tags_list):
        self.tags = json.dumps(tags_list) if tags_list else "[]"

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
    source = Column(String, nullable=True)
    run_type = Column(String, nullable=True)

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, default=1)
    preferred_sources = Column(Text, nullable=True)  # JSON list of source names
    preferred_categories = Column(Text, nullable=True)  # JSON list of category names

    def get_sources(self) -> list:
        if self.preferred_sources:
            return json.loads(self.preferred_sources)
        return []

    def set_sources(self, sources: list):
        self.preferred_sources = json.dumps(sources) if sources else None

    def get_categories(self) -> list:
        if self.preferred_categories:
            return json.loads(self.preferred_categories)
        return []

    def set_categories(self, categories: list):
        self.preferred_categories = json.dumps(categories) if categories else None 

class PipelineFailure(Base):
    __tablename__ = "pipeline_failures"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("posts.id"))
    stage = Column(String)  # 'scrape' or 'tag'
    error_message = Column(Text)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now()) 

class SavedPost(Base):
    __tablename__ = "saved_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post") 