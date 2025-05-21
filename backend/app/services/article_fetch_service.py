from sqlalchemy.orm import Session
from backend.app.db.models import Post
from datetime import datetime

class ArticleFetchService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def fetch_articles(self, source: str, start_date: str, end_date: str):
        # Validate date format
        try:
            date_start = datetime.strptime(start_date, "%Y-%m-%d")
            date_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            raise ValueError(f"start_date and end_date must be in YYYY-MM-DD format. Got start_date='{start_date}', end_date='{end_date}'")
        return self.db_session.query(Post).filter(
            Post.source == source,
            Post.timestamp >= date_start,
            Post.timestamp <= date_end
        ).all() 