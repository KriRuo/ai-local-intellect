from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from .scrapers import rss_scraper
from .db.models import Base, Post
from .db.database import engine, get_db, SessionLocal
from sqlalchemy.orm import Session
import logging
import os
import json
import subprocess

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Local Intellect Scraper API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Automatically import all RSS feeds on startup
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
            rss_scraper.scrape_and_save_rss_feed(db, url, source, platform)
            logging.info(f"Saved feed: {source} ({url})")
            imported_count += 1
        except Exception as e:
            logging.warning(f"Failed to import {source} ({url}): {e}")
            failed_count += 1
    db.close()
    logging.info(f"RSS import complete. Imported: {imported_count}, Skipped: {skipped_count}, Failed: {failed_count}, Total: {len(feeds)}.")

@app.get("/api/scrape/rss")
async def scrape_rss(url: str, source: str, platform: str = "RSS"):
    try:
        posts = rss_scraper.scrape_rss_feed(url, source, platform)
        return {"status": "success", "data": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/rss/save")
def scrape_and_save_rss(
    url: str, source: str, platform: str = "RSS", db: Session = Depends(get_db)
):
    from .scrapers.rss_scraper import scrape_and_save_rss_feed
    try:
        posts = scrape_and_save_rss_feed(db, url, source, platform)
        return {"status": "success", "data": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.timestamp.desc()).all()
    logging.info(f"Fetched {len(posts)} posts from the database.")
    # Convert SQLAlchemy objects to dicts for JSON serialization
    def post_to_dict(post):
        return {
            "id": post.id,
            "source": post.source,
            "platform": post.platform,
            "url": post.url,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "timestamp": post.timestamp.isoformat() if post.timestamp else None,
            "thumbnail": post.thumbnail,
            "author": post.author,
        }
    return {"status": "success", "data": [post_to_dict(p) for p in posts]}

@app.post("/api/scrape/rss/trigger")
def trigger_rss_scraper():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "run_rss_scraper.py")
        subprocess.Popen(["python", script_path])
        return {"status": "started", "message": "RSS scraping script triggered."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 