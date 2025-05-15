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
- `GET /api/scrape/rss` — Scrape an RSS feed (query params: url, source, platform)
- `POST /api/scrape/rss/save` — Scrape and save an RSS feed (JSON body)
- `POST /api/scrape/substack/save` — Scrape and save a Substack feed (JSON body)
- `POST /api/saved` — Save a post for the user
- `GET /api/saved` — List saved posts
- `DELETE /api/saved/{post_id}` — Remove a saved post
- `GET /health` — Health check endpoint

---

**Not yet implemented (listed for future reference):**
- `GET /api/rss-runs` — (TODO)
- `POST /api/scrape/rss/trigger` — (TODO)
- `GET /api/scrape/substack` — (TODO)

See the FastAPI code in `app/main.py` for full details and request/response formats.

## Data Files

- `rss_feeds.json`: Stores scraped RSS feed posts. See `rss_feeds_README.md` for format.
- `rss_sources.json`: Stores the list of RSS sources. See `rss_sources.README.txt` for format.

## Notes

- The backend will attempt to import all RSS sources from `rss_sources.json` on startup.
- Logs are written to `backend/app/logs/backend.log`.
- For development, CORS is enabled for `http://localhost:5173` and `http://localhost:5174`.

## Backend Test Coverage

Automated tests are provided for the main API endpoints and error handling. All tests are located in `backend/app/tests/` and use `pytest` with FastAPI's TestClient.

**Current Coverage:**
- `test_health.py`: Tests the /health endpoint for status and response structure.
- `test_posts.py`: Tests GET /api/posts (empty and not found cases). Stubs for create/update/delete.
- `test_preferences.py`: Tests GET /api/preferences. Stubs for updating preferences.
- `test_saved_content.py`: Tests GET /api/saved. Stubs for saving and deleting content.
- `test_error_handling.py`: Tests 404 error for unknown routes.
- Additional files cover RSS/web feeds, tagging, scrapers, and models.

**Limitations:**
- Most tests only cover successful GET requests and basic error cases.
- No tests for authentication, authorization, or edge cases.
- Many POST/PUT/DELETE tests are stubbed or commented out.
- No tests for database migrations or background jobs.

**Recommendations:**
- Add tests for POST, PUT, DELETE, and PATCH endpoints.
- Test authentication, authorization, and permission errors.
- Add tests for edge cases, invalid input, and error handling.
- Include tests for background jobs, scrapers, and data migrations if applicable.

To run backend tests:
```sh
cd backend
pytest
``` 