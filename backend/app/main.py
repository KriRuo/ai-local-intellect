from fastapi import FastAPI, HTTPException, Depends, Body, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from .scrapers import rss_scraper, substack_scraper
from .db.models import Base, Post, RssScrapeRun, UserPreferences, SavedPost, Note
from .db.database import engine, get_db, SessionLocal
from sqlalchemy.orm import Session
import logging
import os
import json
import subprocess
from pydantic import BaseModel, Field
from .scrapers.rss_scraper import RSSFeedError, InvalidFeedURLError, FeedParsingError, NoEntriesFoundError
import sys
from fastapi.responses import PlainTextResponse
import threading
from .services.tagging_service import TaggingService
import atexit
import time
import signal
import queue
from .utils.pipeline_logger import PipelineLogger
from .services.openai_client import OpenAIClient
import asyncio
from backend.app.services.article_fetch_service import ArticleFetchService
from backend.app.services.article_summarization_service import ArticleSummarizationService
from backend.app.services.summary_storage_service import SummaryStorageService
from backend.app.services.article_batch_summarization_service import ArticleBatchSummarizationService
import traceback
from datetime import datetime
import feedparser

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Local Intellect Scraper API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],  # Allow both dev ports and specified frontend
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

# Initialize the OpenAI client (replace LM Studio client)
lm_client = OpenAIClient()

# Initialize new services
article_fetch_service = ArticleFetchService(SessionLocal())
article_summarization_service = ArticleSummarizationService(lm_client)
summary_storage_service = SummaryStorageService(SessionLocal())
batch_summarization_service = ArticleBatchSummarizationService(
    article_fetch_service, article_summarization_service, summary_storage_service
)

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
    # Add this line to close the LM Studio client
    asyncio.run(lm_client.close())

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
    logger.info("POST /api/scrape/rss/import-all called")
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
    """
    Request model for submitting an RSS feed to be scraped and/or saved.
    Attributes:
        url: The RSS feed URL.
        source: The source or publisher name.
        platform: The platform type (default: 'RSS').
    """
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
    logger.info("GET /api/scrape/rss called")
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
    logger.info("POST /api/scrape/rss/save called")
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
        "tag_status": post.tag_status,
    }

@app.get("/api/posts")
def get_posts(db: Session = Depends(get_db)):
    logger.info("GET /api/posts called")
    posts = db.query(Post).order_by(Post.timestamp.desc()).all()
    logging.info(f"Fetched {len(posts)} posts from the database.")
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
    logger.info("POST /api/scrape/rss/trigger called")
    try:
        subprocess.Popen([sys.executable, "-m", "backend.app.run_rss_scraper"])
        return {"status": "started", "message": "RSS scraping script triggered."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rss-sources")
def get_rss_sources():
    logger.info("GET /api/rss-sources called")
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
    logger.info("GET /api/rss-runs called")
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
    logger.info("GET /api/scrape/substack called")
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
    logger.info("POST /api/scrape/substack/save called")
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
    logger.info("GET /health called")
    return {"status": "ok"}

@app.get("/api/rss-runs/{run_id}/skipped-sources-md", response_class=PlainTextResponse)
def export_skipped_sources_markdown(run_id: int, db: Session = Depends(get_db)):
    logger.info(f"GET /api/rss-runs/{run_id}/skipped-sources-md called")
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
    status_filter: str = "pending",
    db: Session = Depends(get_db)
):
    logger.info("POST /api/tag-new-posts called")
    """
    Tag posts using the TaggingService.
    Args:
        batch_size: Number of posts to process per call (default 10)
        status_filter: Filter posts by tag_status ("pending" or "error")
    Returns:
        dict: Tagging statistics
    """
    tagging_service = TaggingService()
    stats = tagging_service.tag_new_posts(
        db,
        batch_size=batch_size,
        status_filter=status_filter
    )
    return {"status": "success", "data": stats}

@app.post("/api/retry-failed-tags")
def retry_failed_tags_endpoint(
    batch_size: int = 10,
    db: Session = Depends(get_db)
):
    logger.info("POST /api/retry-failed-tags called")
    """
    Retry tagging for posts that previously failed.
    Args:
        batch_size: Number of posts to process per call (default 10)
    Returns:
        dict: Tagging statistics
    """
    tagging_service = TaggingService()
    stats = tagging_service.retry_failed_tags(db, batch_size=batch_size)
    return {"status": "success", "data": stats}

@app.get("/api/tagging-stats")
def get_tagging_stats(db: Session = Depends(get_db)):
    logger.info("GET /api/tagging-stats called")
    """
    Get statistics about post tagging status.
    Returns:
        dict: Counts of posts by tag_status
    """
    stats = {
        "pending": db.query(Post).filter(Post.tag_status == "pending").count(),
        "tagged": db.query(Post).filter(Post.tag_status == "tagged").count(),
        "error": db.query(Post).filter(Post.tag_status == "error").count(),
    }
    return {"status": "success", "data": stats}

class PreferencesRequest(BaseModel):
    """
    Request model for setting user preferences.
    Attributes:
        preferred_sources: List of preferred news sources.
        preferred_categories: List of preferred news categories.
    """
    preferred_sources: list[str]
    preferred_categories: list[str]

class PreferencesResponse(BaseModel):
    """
    Response model for returning user preferences.
    Attributes:
        preferred_sources: List of preferred news sources.
        preferred_categories: List of preferred news categories.
    """
    preferred_sources: list[str]
    preferred_categories: list[str]

# --- USER PREFERENCES ENDPOINTS ---
@app.get("/api/preferences", response_model=PreferencesResponse)
def get_preferences(db: Session = Depends(get_db)):
    logger.info("GET /api/preferences called")
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
    logger.info("POST /api/preferences called")
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

class SavedPostRequest(BaseModel):
    """
    Request model for saving a post.
    Attributes:
        post_id: The ID of the post to save.
    """
    post_id: int

class SavedPostResponse(BaseModel):
    """
    Response model for a saved post.
    Attributes:
        id: Unique identifier for the saved post record.
        post_id: The ID of the original post.
        saved_at: ISO timestamp when the post was saved.
        post: Dictionary representation of the saved post.
    """
    id: int
    post_id: int
    saved_at: str
    post: dict

@app.post("/api/saved", response_model=SavedPostResponse)
def save_post(req: SavedPostRequest, db: Session = Depends(get_db)):
    logger.info("POST /api/saved called")
    post = db.query(Post).filter(Post.id == req.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    saved_post = SavedPost(post_id=post.id)
    db.add(saved_post)
    db.commit()
    db.refresh(saved_post)
    return {
        "id": saved_post.id,
        "post_id": saved_post.post_id,
        "saved_at": saved_post.saved_at.isoformat(),
        "post": post_to_dict(post)
    }

@app.get("/api/saved", response_model=List[SavedPostResponse])
def get_saved_posts(db: Session = Depends(get_db)):
    logger.info("GET /api/saved called")
    saved_posts = db.query(SavedPost).order_by(SavedPost.saved_at.desc()).all()
    result = []
    for saved in saved_posts:
        post = db.query(Post).filter(Post.id == saved.post_id).first()
        if post:
            result.append({
                "id": saved.id,
                "post_id": saved.post_id,
                "saved_at": saved.saved_at.isoformat(),
                "post": post_to_dict(post)
            })
    return result

@app.delete("/api/saved/{post_id}")
def delete_saved_post(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /api/saved/{post_id} called")
    saved_posts = db.query(SavedPost).filter(SavedPost.post_id == post_id).all()
    if not saved_posts:
        raise HTTPException(status_code=404, detail="Saved post not found")
    for saved in saved_posts:
        db.delete(saved)
    db.commit()
    return {"detail": "Deleted"}

def run_full_pipeline(db: Session):
    """
    Orchestrate the full pipeline: scrape all RSS feeds, then tag new posts.
    Returns a summary of both steps.
    """
    logger.info("Starting full pipeline: scrape all RSS feeds, then tag new posts.")
    summary = {"scraping": {}, "tagging": {}, "errors": []}
    try:
        pipeline_logger = PipelineLogger(db)
        run = pipeline_logger.start_run(source="pipeline", run_type="full_pipeline")
        logger.info(f"Pipeline run started with id: {run.id}")
    except Exception as e:
        logger.error(f"Failed to start pipeline run: {e}", exc_info=True)
        raise

    try:
        # Scrape all RSS feeds
        rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
        if not os.path.exists(rss_sources_path):
            pipeline_logger.end_run(status="error", error_message="rss_sources.json not found")
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
            article = {"url": url, "source": source, "platform": platform}
            if not url or not source:
                logger.warning(f"Skipped feed due to missing url or source: {feed}")
                skipped_count += 1
                pipeline_logger.log_article_processed(article, status="skipped", stage="scraping", error_message="Missing url or source")
                continue
            logger.info(f"Fetching RSS feed: {source} ({url}) ...")
            try:
                from .scrapers import rss_scraper
                rss_scraper.scrape_and_save_rss_feed(db, url, source, platform)
                logger.info(f"Saved feed: {source} ({url})")
                imported_count += 1
                pipeline_logger.log_article_processed(article, status="success", stage="scraping")
            except Exception as e:
                logger.warning(f"Failed to import {source} ({url}): {e}")
                failed_count += 1
                failed_feeds.append({"source": source, "url": url, "error": str(e)})
                pipeline_logger.log_article_processed(article, status="error", stage="scraping", error_message=str(e))
        summary["scraping"] = {
            "imported": imported_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "total": len(feeds),
            "failed_feeds": failed_feeds
        }
    except Exception as e:
        logger.error(f"Pipeline scraping step failed: {e}")
        summary["errors"].append(f"Scraping step failed: {str(e)}")
        pipeline_logger.end_run(status="error", error_message=str(e))
        logger.info(f"Pipeline run with id {run.id} ended with error.")
        return {"status": "error", "summary": summary}

    try:
        # Tag new posts
        from .services.tagging_service import TaggingService
        tagging_service = TaggingService()
        tagging_stats = tagging_service.tag_new_posts(db, batch_size=1000, status_filter="pending")
        summary["tagging"] = tagging_stats
        pipeline_logger.end_run(status="completed")
        logger.info(f"Pipeline run with id {run.id} completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline tagging step failed: {e}")
        summary["errors"].append(f"Tagging step failed: {str(e)}")
        pipeline_logger.end_run(status="error", error_message=str(e))
        logger.info(f"Pipeline run with id {run.id} ended with error.")
        return {"status": "error", "summary": summary}

    logger.info("Pipeline completed successfully.")
    return {"status": "success", "summary": summary}

@app.post("/api/pipeline/refresh-all")
def refresh_all_pipeline(db: Session = Depends(get_db)):
    logger.info("POST /api/pipeline/refresh-all called")
    logger.info("[refresh_all_pipeline] Entered endpoint.")
    if db is None:
        logger.error("[refresh_all_pipeline] DB session is None!")
    else:
        logger.info("[refresh_all_pipeline] DB session received.")
    logger.info("[refresh_all_pipeline] About to instantiate PipelineLogger.")
    try:
        pipeline_logger = PipelineLogger(db)
        logger.info("[refresh_all_pipeline] PipelineLogger instantiated.")
    except Exception as e:
        logger.error(f"[refresh_all_pipeline] Failed to instantiate PipelineLogger: {e}", exc_info=True)
        raise
    # Call the actual pipeline logic
    return run_full_pipeline(db)

# Add these new models after the other model definitions
class SummaryRequest(BaseModel):
    text: str
    max_tokens: int = 150

class PromptRequest(BaseModel):
    prompt: str
    system_prompt: str = None

# Add these new endpoints before the health check endpoint
@app.post("/api/lm/summarize")
async def summarize_text(request: SummaryRequest):
    logger.info("POST /api/lm/summarize called")
    try:
        summary = await lm_client.generate_summary(request.text, request.max_tokens)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-alive")
def test_alive():
    logger.info("GET /test-alive called")
    return {"status": "alive"} 

@app.post("/api/lm/generate")
async def generate_response(request: PromptRequest):
    logger.info("POST /api/lm/generate called")
    try:
        response = await lm_client.generate_response(
            request.prompt,
            request.system_prompt
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SummarizationRequest(BaseModel):
    sources: List[str]
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    combined: bool = False

@app.post("/api/lm/summarize-articles")
async def summarize_articles(request: SummarizationRequest):
    logger.info(f"/api/lm/summarize-articles called with: sources={request.sources}, start_date={request.start_date}, end_date={request.end_date}, combined={request.combined}")
    try:
        if request.combined:
            logger.info("Calling summarize_articles_combined (single grouped summary)")
            # Fetch articles for logging
            all_posts = []
            for source in request.sources:
                posts = batch_summarization_service.fetch_service.fetch_articles(source, request.start_date, request.end_date)
                all_posts.extend(posts)
            logger.info(f"Fetched {len(all_posts)} articles for combined summary.")
            for idx, post in enumerate(all_posts, 1):
                logger.info(f"Article {idx}: Title='{getattr(post, 'title', '')}', Source='{getattr(post, 'source', '')}', Date='{getattr(post, 'timestamp', '')}'")
            # Build the prompt for logging (same as in summarize_articles_combined)
            prompt_lines = []
            for idx, post in enumerate(all_posts, 1):
                prompt_lines.append(f"Article {idx}:")
                prompt_lines.append(f"Source: {getattr(post, 'source', '')}")
                prompt_lines.append(f"URL: {getattr(post, 'url', '')}")
                prompt_lines.append(f"Publish Date: {getattr(post, 'timestamp', '')}")
                prompt_lines.append(f"Title: {getattr(post, 'title', '')}")
                prompt_lines.append(f"Content: {getattr(post, 'content', '')}")
                prompt_lines.append(f"Author: {getattr(post, 'author', '')}")
                prompt_lines.append("")
            prompt = "\n".join(prompt_lines)
            logger.info(f"Combined prompt sent to model:\n{prompt}")
            summary = await batch_summarization_service.summarize_articles_combined(
                request.sources, request.start_date, request.end_date
            )
            return {"summary": summary}
        else:
            logger.info("Calling summarize_articles (per-article summaries)")
            # Fetch articles for logging
            all_posts = []
            for source in request.sources:
                posts = batch_summarization_service.fetch_service.fetch_articles(source, request.start_date, request.end_date)
                all_posts.extend(posts)
            logger.info(f"Fetched {len(all_posts)} articles for per-article summaries.")
            for idx, post in enumerate(all_posts, 1):
                logger.info(f"Article {idx}: Title='{getattr(post, 'title', '')}', Source='{getattr(post, 'source', '')}', Date='{getattr(post, 'timestamp', '')}'")
            summaries = await batch_summarization_service.summarize_articles(
                request.sources, request.start_date, request.end_date
            )
            return {"summaries": summaries}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

class NoteCreate(BaseModel):
    title: str
    description: str = None

class NoteUpdate(BaseModel):
    title: str = None
    description: str = None

class NoteResponse(BaseModel):
    id: int
    title: str
    description: str = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class NotesListResponse(BaseModel):
    status: str
    data: List[NoteResponse]

    class Config:
        from_attributes = True

@app.get("/api/notes", response_model=NotesListResponse)
def get_notes(db: Session = Depends(get_db)):
    logger.info("GET /api/notes called")
    try:
        notes = db.query(Note).order_by(Note.created_at.desc()).all()
        return {"status": "success", "data": [NoteResponse.from_orm(n) for n in notes]}
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/api/notes", response_model=NoteResponse)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    try:
        db_note = Note(title=note.title, description=note.description)
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.description is not None:
        db_note.description = note_update.description
    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}

class RSSSourceRequest(BaseModel):
    source: str = Field(..., description="Name of the source")
    url: str = Field(..., description="RSS feed URL")
    platform: str = Field("RSS", description="Platform type (default: RSS)")
    category: str = Field(None, description="Category of the source")
    description: str = Field(None, description="Description of the source")
    source_type: str = Field(None, description="Type of source (e.g., Industry, Academic)")

@app.post("/api/rss-sources")
def add_rss_source(req: RSSSourceRequest):
    """
    Add a new RSS source to rss_sources.json after validating the feed URL.
    """
    logger.info(f"POST /api/rss-sources called with: {req}")
    # Validate the RSS feed URL
    try:
        feed = feedparser.parse(req.url)
        if feed.bozo:
            raise HTTPException(status_code=400, detail=f"Invalid RSS feed: {feed.bozo_exception}")
        if not hasattr(feed, 'entries') or not feed.entries:
            raise HTTPException(status_code=400, detail="No entries found in the RSS feed.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse RSS feed: {str(e)}")

    # Load existing sources
    rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
    if not os.path.exists(rss_sources_path):
        raise HTTPException(status_code=404, detail="rss_sources.json not found")
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    # Check for duplicate URL
    if any(s.get('url') == req.url for s in sources):
        raise HTTPException(status_code=400, detail="This RSS feed URL is already in the sources list.")
    # Append new source
    new_source = req.dict(exclude_none=True)
    sources.append(new_source)
    with open(rss_sources_path, 'w', encoding='utf-8') as f:
        json.dump(sources, f, indent=4, ensure_ascii=False)
    logger.info(f"Added new RSS source: {new_source}")
    return {"status": "success", "data": new_source}

@app.put("/api/rss-sources/{url}")
def update_rss_source(
    url: str = Path(..., description="Current URL of the RSS source to update"),
    req: RSSSourceRequest = Body(...)
):
    """
    Update an existing RSS source in rss_sources.json.
    If the URL is changed, validate the new URL and check for duplicates.
    """
    logger.info(f"PUT /api/rss-sources/{url} called with: {req}")
    rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
    if not os.path.exists(rss_sources_path):
        raise HTTPException(status_code=404, detail="rss_sources.json not found")
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    # Find the source by current URL
    idx = next((i for i, s in enumerate(sources) if s.get('url') == url), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="RSS source not found.")
    # If URL is changed, check for duplicate and validate new feed
    if req.url != url:
        if any(s.get('url') == req.url for s in sources):
            raise HTTPException(status_code=400, detail="This new RSS feed URL is already in the sources list.")
        try:
            feed = feedparser.parse(req.url)
            if feed.bozo:
                raise HTTPException(status_code=400, detail=f"Invalid RSS feed: {feed.bozo_exception}")
            if not hasattr(feed, 'entries') or not feed.entries:
                raise HTTPException(status_code=400, detail="No entries found in the RSS feed.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse RSS feed: {str(e)}")
    # Update the source
    sources[idx] = req.dict(exclude_none=True)
    with open(rss_sources_path, 'w', encoding='utf-8') as f:
        json.dump(sources, f, indent=4, ensure_ascii=False)
    logger.info(f"Updated RSS source: {sources[idx]}")
    return {"status": "success", "data": sources[idx]}

@app.post("/api/rss-sources/bulk-import")
async def bulk_import_rss_sources(request: Request):
    """
    Bulk import RSS sources from a JSON array. Each source must match the RSSSourceRequest schema.
    Returns a summary of added, skipped, and errored sources.
    """
    logger.info("POST /api/rss-sources/bulk-import called")
    rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
    if not os.path.exists(rss_sources_path):
        raise HTTPException(status_code=404, detail="rss_sources.json not found")
    with open(rss_sources_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    existing_urls = {s.get('url') for s in sources}
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Input must be a JSON array of sources.")
    added = 0
    skipped = 0
    errors = []
    for idx, item in enumerate(data):
        try:
            # Validate required fields
            src = RSSSourceRequest(**item)
            # Check for duplicate
            if src.url in existing_urls:
                skipped += 1
                continue
            # Validate RSS feed URL
            feed = feedparser.parse(src.url)
            if feed.bozo:
                raise Exception(f"Invalid RSS feed: {feed.bozo_exception}")
            if not hasattr(feed, 'entries') or not feed.entries:
                raise Exception("No entries found in the RSS feed.")
            # Add to sources
            sources.append(src.dict(exclude_none=True))
            existing_urls.add(src.url)
            added += 1
        except Exception as e:
            errors.append({"index": idx, "source": item, "error": str(e)})
    with open(rss_sources_path, 'w', encoding='utf-8') as f:
        json.dump(sources, f, indent=4, ensure_ascii=False)
    logger.info(f"Bulk import complete. Added: {added}, Skipped: {skipped}, Errors: {len(errors)}")
    return {"status": "success", "added": added, "skipped": skipped, "errors": errors}
