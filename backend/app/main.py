from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from .scrapers import rss_scraper, substack_scraper
from .db.models import Base, Post, RssScrapeRun, UserPreferences
from .db.database import engine, get_db, SessionLocal
from sqlalchemy.orm import Session
import logging
import os
import json
import subprocess
from pydantic import BaseModel
from .scrapers.rss_scraper import RSSFeedError, InvalidFeedURLError, FeedParsingError, NoEntriesFoundError
import sys
from fastapi.responses import PlainTextResponse
import threading
from .services.tagging_service import TaggingService
import atexit
import time
import signal
import queue

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Local Intellect Scraper API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Allow both dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'backend.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
running = True
input_queue = queue.Queue()

def signal_handler(signum, frame):
    global running
    running = False
    logger.info(f"Received signal {signum}")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def cleanup():
    global running
    running = False
    logger.info("Cleaning up resources...")

atexit.register(cleanup)

def input_thread():
    while running:
        try:
            choice = input("\nEnter your choice (0-3): ")
            input_queue.put(choice)
        except EOFError:
            break

def run_menu():
    global running
    
    # Start input thread
    input_handler = threading.Thread(target=input_thread)
    input_handler.daemon = True
    input_handler.start()
    
    while running:
        try:
            print("\nBackend is running!")
            print("\nPlease select an option:")
            print("0. Run all")
            print("1. Run RSS scraping")
            print("2. Run Tagging service")
            print("3. Exit")
            print()
            
            try:
                choice = input_queue.get(timeout=1)
            except queue.Empty:
                continue
                
            if choice == "0":
                print("Running RSS scraping...")
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
                print("Starting post tagging process...")
                subprocess.Popen([sys.executable, "-m", "backend.app.scripts.tag_posts"])
            elif choice == "1":
                print("Running RSS scraping...")
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
            elif choice == "2":
                print("Starting post tagging process...")
                subprocess.Popen([sys.executable, "-m", "backend.app.scripts.tag_posts"])
            elif choice == "3":
                print("Exiting...")
                running = False
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            logger.error(f"Menu thread error: {e}")
            break

# Start the menu in a separate thread
menu_thread = threading.Thread(target=run_menu)
menu_thread.daemon = True
menu_thread.start()

logger.info("🚀 FastAPI backend is starting up...")

# Remove the automatic RSS feed importing code and add a new endpoint
@app.post("/api/scrape/rss/import-all")
def import_all_rss_feeds(db: Session = Depends(get_db)):
    """
    Import all RSS feeds defined in rss_sources.json
    """
    rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
    if not os.path.exists(rss_sources_path):
        raise HTTPException(status_code=404, detail="rss_sources.json not found")
    
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    failed_feeds = []
    
    for feed in feeds:
        url = feed.get('url')
        source = feed.get('source')
        platform = feed.get('platform', 'RSS')
        if not url or not source:
            logger.warning(f"Skipped feed due to missing url or source: {feed}")
            skipped_count += 1
            continue
        logger.info(f"Fetching RSS feed: {source} ({url}) ...")
        try:
            rss_scraper.scrape_and_save_rss_feed(db, url, source, platform)
            logger.info(f"Saved feed: {source} ({url})")
            imported_count += 1
        except Exception as e:
            logger.warning(f"Failed to import {source} ({url}): {e}")
            failed_count += 1
            failed_feeds.append({"source": source, "url": url, "error": str(e)})
    
    return {
        "status": "success",
        "data": {
            "imported": imported_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "total": len(feeds),
            "failed_feeds": failed_feeds
        }
    }

class RSSRequest(BaseModel):
    url: str
    source: str
    platform: str = "RSS"

    @classmethod
    def validate_url(cls, url: str):
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return url

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_url

@app.get("/api/scrape/rss")
async def scrape_rss(url: str, source: str, platform: str = "RSS"):
    """
    Scrape posts from an RSS feed without saving them.
    """
    try:
        posts = rss_scraper.scrape_rss_feed(url, source, platform)
        return {"status": "success", "data": posts}
    except Exception as e:
        logger.error(f"Error scraping RSS feed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/rss/save")
def scrape_and_save_rss(req: RSSRequest, db: Session = Depends(get_db)):
    """
    Scrape posts from an RSS feed and save them to the database.
    """
    try:
        posts = rss_scraper.scrape_and_save_rss_feed(db, req.url, req.source, req.platform)
        return {"status": "success", "data": posts}
    except rss_scraper.InvalidFeedURLError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except rss_scraper.FeedParsingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except rss_scraper.NoEntriesFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except rss_scraper.RSSFeedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in RSS scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.timestamp.desc()).all()
    logging.info(f"Fetched {len(posts)} posts from the database.")
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
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            "tags": post.get_tags() if hasattr(post, 'get_tags') else [],
            "category": post.category,
        }
    if posts:
        return {"status": "success", "data": [post_to_dict(p) for p in posts]}
    # Fallback to rss_feeds.json if DB is empty
    rss_feeds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_feeds.json')
    if os.path.exists(rss_feeds_path):
        with open(rss_feeds_path, 'r', encoding='utf-8') as f:
            feeds_data = json.load(f)
            return {"status": "success", "data": feeds_data.get("posts", [])}
    return {"status": "success", "data": []}

@app.post("/api/scrape/rss/trigger")
def trigger_rss_scraper():
    try:
        subprocess.Popen([sys.executable, "-m", "backend.app.run_rss_scraper"])
        return {"status": "started", "message": "RSS scraping script triggered."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rss-sources")
def get_rss_sources():
    """
    Get the list of available RSS sources from rss_sources.json
    """
    rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
    if not os.path.exists(rss_sources_path):
        raise HTTPException(status_code=404, detail="rss_sources.json not found")
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        feeds = json.load(f)
    return {"status": "success", "data": feeds}

@app.get("/api/rss-runs")
def get_rss_runs(db: Session = Depends(get_db)):
    try:
        logging.info("📥 /api/rss-runs endpoint was called")
        runs = db.query(RssScrapeRun).order_by(RssScrapeRun.started_at.desc()).limit(50).all()
        logging.info(f"Found {len(runs)} RSS scrape runs in the database.")
        def run_to_dict(run):
            return {
                "id": run.id,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "ended_at": run.ended_at.isoformat() if run.ended_at else None,
                "duration_seconds": run.duration_seconds,
                "num_sources_total": run.num_sources_total,
                "num_sources_skipped": run.num_sources_skipped,
                "num_sources_captured": run.num_sources_captured,
                "num_articles_captured": run.num_articles_captured,
                "status": run.status,
                "error_message": run.error_message,
            }
        return {"status": "success", "data": [run_to_dict(r) for r in runs]}
    except Exception as e:
        logging.error(f"Error in /api/rss-runs: {e}")
        raise 

@app.get("/api/scrape/substack")
async def scrape_substack(url: str):
    try:
        articles = substack_scraper.scrape_substack_articles(url)
        return {"status": "success", "data": articles}
    except substack_scraper.SubstackScraperError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/substack/save")
def scrape_and_save_substack(
    url: str,
    db: Session = Depends(get_db)
):
    try:
        posts = substack_scraper.scrape_and_save_substack(db, url)
        return {"status": "success", "data": [
            {
                "id": p.id,
                "source": p.source,
                "platform": p.platform,
                "url": p.url,
                "title": p.title,
                "content": p.content,
                "summary": p.summary,
                "timestamp": p.timestamp.isoformat() if p.timestamp else None,
                "thumbnail": p.thumbnail,
                "author": p.author,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            } for p in posts
        ]}
    except substack_scraper.SubstackScraperError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/rss-runs/{run_id}/skipped-sources-md", response_class=PlainTextResponse)
def export_skipped_sources_markdown(run_id: int, db: Session = Depends(get_db)):
    run = db.query(RssScrapeRun).filter(RssScrapeRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="RSS run not found")
    if not run.skipped_sources_details:
        return "# Skipped Sources\n\nNo skipped sources for this run."
    try:
        skipped = json.loads(run.skipped_sources_details)
    except Exception:
        return "# Skipped Sources\n\nCould not parse skipped sources details."
    if not skipped:
        return "# Skipped Sources\n\nNo skipped sources for this run."
    md = ["# Skipped Sources\n", "| Source | URL | Reason |", "|--------|-----|--------|"]
    for item in skipped:
        src = (item.get("source") or "-").replace("|", "\\|")
        url = (item.get("url") or "-").replace("|", "\\|")
        reason = (item.get("reason") or "-").replace("|", "\\|").replace("\n", " ")
        md.append(f"| {src} | {url} | {reason} |")
    return "\n".join(md)

@app.post("/api/tag-new-posts")
def tag_new_posts_endpoint(
    batch_size: int = 10,
    time_window: int = 5,
    db: Session = Depends(get_db)
):
    """
    Tag new posts using the Llama 4 Maverick API via TaggingService.
    - batch_size: number of posts to process per call (default 10)
    - time_window: number of minutes to look back for new posts (default 5)
    Returns tagging statistics.
    """
    tagging_service = TaggingService()
    stats = tagging_service.tag_new_posts(db, batch_size=batch_size, time_window=time_window)
    return {"status": "success", "data": stats}

class PreferencesRequest(BaseModel):
    preferred_sources: list[str]
    preferred_categories: list[str]

class PreferencesResponse(BaseModel):
    preferred_sources: list[str]
    preferred_categories: list[str]

# --- USER PREFERENCES ENDPOINTS ---
@app.get("/api/preferences", response_model=PreferencesResponse)
def get_preferences(db: Session = Depends(get_db)):
    prefs = db.query(UserPreferences).get(1)
    if not prefs:
        # Return empty preferences if not set
        return PreferencesResponse(preferred_sources=[], preferred_categories=[])
    return PreferencesResponse(
        preferred_sources=prefs.get_sources(),
        preferred_categories=prefs.get_categories()
    )

@app.post("/api/preferences", response_model=PreferencesResponse)
def set_preferences(
    req: PreferencesRequest = Body(...),
    db: Session = Depends(get_db)
):
    prefs = db.query(UserPreferences).get(1)
    if not prefs:
        prefs = UserPreferences(id=1)
        db.add(prefs)
    prefs.set_sources(req.preferred_sources)
    prefs.set_categories(req.preferred_categories)
    db.commit()
    return PreferencesResponse(
        preferred_sources=prefs.get_sources(),
        preferred_categories=prefs.get_categories()
    ) 