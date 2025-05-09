# AI Insight Tracker Backend

## Overview

This is the backend service for the AI Insight Tracker app. It is built with FastAPI and provides API endpoints for aggregating, scraping, and serving AI news articles and sources.

## Setup & Installation

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Backend

Start the FastAPI server with:
```sh
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8081 (or your configured port).

## Environment Variables

- The backend can be configured with environment variables for database and other settings. (Default: SQLite in the project directory)
- The frontend expects the backend URL to be set in `VITE_API_URL`.

## API Endpoints

- `GET /api/posts` — Get all posts
- `GET /api/rss-sources` — Get all RSS sources
- `GET /api/rss-runs` — Get recent RSS scrape runs
- `GET /api/scrape/rss` — Scrape an RSS feed (query params: url, source, platform)
- `POST /api/scrape/rss/save` — Scrape and save an RSS feed (JSON body)
- `POST /api/scrape/rss/trigger` — Trigger the RSS scraping script
- `GET /api/scrape/substack` — Scrape a Substack feed (query param: url)
- `POST /api/scrape/substack/save` — Scrape and save a Substack feed (JSON body)
- `GET /health` — Health check endpoint

See the FastAPI code in `app/main.py` for full details and request/response formats.

## Data Files

- `rss_feeds.json`: Stores scraped RSS feed posts. See `rss_feeds_README.md` for format.
- `rss_sources.json`: Stores the list of RSS sources. See `rss_sources.README.txt` for format.

## Notes

- The backend will attempt to import all RSS sources from `rss_sources.json` on startup.
- Logs are written to `backend/app/logs/backend.log`.
- For development, CORS is enabled for `http://localhost:5173` and `http://localhost:5174`. 