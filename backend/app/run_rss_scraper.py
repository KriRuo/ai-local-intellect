import os
import json
import logging
import sys
from datetime import datetime, timezone
from backend.app.db.database import SessionLocal
from backend.app.db.models import RssScrapeRun
from backend.app.scrapers.rss_scraper import scrape_and_save_rss_feed

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'rss_scraper.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
if os.path.exists(rss_sources_path):
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    db = SessionLocal()
    run = RssScrapeRun(
        started_at=datetime.utcnow(),
        num_sources_total=len(feeds),
        status="running"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    article_count = 0
    start_time = datetime.utcnow()
    try:
        for feed in feeds:
            url = feed.get('url')
            source = feed.get('source')
            platform = feed.get('platform', 'RSS')
            if not url or not source:
                logging.warning(f"Skipped feed due to missing url or source: {feed}")
                skipped_count += 1
                continue
            logging.info(f"Fetching RSS feed: {source} ({url}) ...")
            try:
                posts = scrape_and_save_rss_feed(db, url, source, platform)
                article_count += len(posts) if posts else 0
                logging.info(f"Saved feed: {source} ({url})")
                imported_count += 1
            except Exception as e:
                logging.warning(f"Failed to import {source} ({url}): {e}")
                failed_count += 1
        end_time = datetime.utcnow()
        run.ended_at = end_time
        run.duration_seconds = (end_time - start_time).total_seconds()
        run.num_sources_skipped = skipped_count + failed_count
        run.num_sources_captured = imported_count
        run.num_articles_captured = article_count
        run.status = "completed"
        run.error_message = None
        db.commit()
        logging.info(f"RSS import complete. Imported: {imported_count}, Skipped: {skipped_count}, Failed: {failed_count}, Total: {len(feeds)}.")
    except Exception as e:
        end_time = datetime.utcnow()
        run.ended_at = end_time
        run.duration_seconds = (end_time - start_time).total_seconds()
        run.status = "failed"
        run.error_message = str(e)
        db.commit()
        logging.error(f"RSS scraping run failed: {e}")
    finally:
        db.close()
else:
    logging.error(f"rss_sources.json not found at {rss_sources_path}") 