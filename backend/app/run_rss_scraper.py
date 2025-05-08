import os
import json
import logging
from datetime import datetime
from backend.app.db.database import SessionLocal
from backend.app.db.models import RssScrapeRun
from backend.app.scrapers.rss_scraper import scrape_and_save_rss_feed

logging.basicConfig(level=logging.INFO)

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