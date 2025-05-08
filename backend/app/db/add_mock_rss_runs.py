import sys
import os
from datetime import datetime, timedelta

# Ensure the parent directory is in sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.db.database import SessionLocal
from app.db.models import RssScrapeRun

# Create a new database session
session = SessionLocal()

# Create mock runs
def add_mock_runs():
    now = datetime.utcnow()
    runs = [
        RssScrapeRun(
            started_at=now - timedelta(days=2),
            ended_at=now - timedelta(days=2, minutes=-5),
            duration_seconds=300,
            num_sources_total=10,
            num_sources_skipped=2,
            num_sources_captured=8,
            num_articles_captured=25,
            status="completed",
            error_message=None
        ),
        RssScrapeRun(
            started_at=now - timedelta(days=1),
            ended_at=now - timedelta(days=1, minutes=-7),
            duration_seconds=420,
            num_sources_total=12,
            num_sources_skipped=1,
            num_sources_captured=11,
            num_articles_captured=30,
            status="completed",
            error_message=None
        ),
        RssScrapeRun(
            started_at=now - timedelta(hours=12),
            ended_at=now - timedelta(hours=12, minutes=-6),
            duration_seconds=360,
            num_sources_total=15,
            num_sources_skipped=3,
            num_sources_captured=12,
            num_articles_captured=40,
            status="failed",
            error_message="Network error on source 3"
        ),
    ]
    session.add_all(runs)
    session.commit()
    print(f"Inserted {len(runs)} mock rss_scrape_runs.")

if __name__ == "__main__":
    add_mock_runs()
    session.close() 