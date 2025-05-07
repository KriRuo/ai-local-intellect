import os
import json
import logging
from db.database import SessionLocal
from scrapers.rss_scraper import scrape_and_save_rss_feed

logging.basicConfig(level=logging.INFO)

rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
if os.path.exists(rss_sources_path):
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    db = SessionLocal()
    imported_count = 0
    skipped_count = 0
    failed_count = 0
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
            scrape_and_save_rss_feed(db, url, source, platform)
            logging.info(f"Saved feed: {source} ({url})")
            imported_count += 1
        except Exception as e:
            logging.warning(f"Failed to import {source} ({url}): {e}")
            failed_count += 1
    db.close()
    logging.info(f"RSS import complete. Imported: {imported_count}, Skipped: {skipped_count}, Failed: {failed_count}, Total: {len(feeds)}.")
else:
    logging.error(f"rss_sources.json not found at {rss_sources_path}") 