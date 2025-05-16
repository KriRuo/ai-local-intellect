from sqlalchemy.orm import Session
from backend.app.db.models import ArticleSummary

class SummaryStorageService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def store_summary(self, post_id: int, summary: str):
        new_summary = ArticleSummary(post_id=post_id, summary=summary)
        self.db_session.add(new_summary)
        self.db_session.commit()
        return new_summary 