"""
Anthropic News Scraper Module

This module provides functionality to scrape news articles from Anthropic's website.
It handles both English and German date formats, with special attention to German umlauts
and date parsing. The scraper uses Playwright for browser automation and includes
human-like behavior simulation to avoid detection.

Key Features:
- Multi-format date parsing (English and German)
- Robust article extraction with multiple selector fallbacks
- Human-like browsing behavior
- Configurable scraping limits (by time or post count)
- Duplicate detection and content cleaning
"""

import sys
import os
import json
# Add the project root to sys.path for reliable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import random
import time
import re
import unicodedata
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from playwright.sync_api import sync_playwright, TimeoutError
from backend.app.db.models import Post
from backend.app.db.database import SessionLocal
import logging
import argparse

def parse_text_date(date_text: str) -> Optional[datetime]:
    """
    Parse dates with German month names, handling special characters properly.
    
    This function handles various date formats including:
    - German dates with umlauts (e.g., "3. März 2025")
    - English dates (e.g., "24. Feb. 2025")
    - Various month name formats and abbreviations
    
    The parsing process:
    1. Cleans and normalizes the input text
    2. Splits the date into components (day, month, year)
    3. Handles cases where month and year might be combined
    4. Normalizes German month names to English
    5. Handles special characters and umlauts
    6. Formats the date for final parsing
    
    Args:
        date_text (str): Date string to parse (e.g., "3. März 2025")
    
    Returns:
        Optional[datetime]: Parsed datetime object or None if parsing fails
    """
    print(f" Attempting to parse date: {date_text}")
    
    # Clean up the text first
    date_text = date_text.strip()
    print(f" Input text: {date_text}")
    
    try:
        # First split by dots and clean up
        parts = [p.strip() for p in date_text.split('.') if p.strip()]
        print(f" Initial split parts: {parts}")
        
        # Handle case where year might be attached to month
        if len(parts) == 2 and ' ' in parts[1]:
            # Split the second part by space
            month_year = parts[1].split()
            if len(month_year) == 2:
                parts = [parts[0], month_year[0], month_year[1]]
        
        print(f" Processed parts: {parts}")
        
        if len(parts) >= 3:
            day, month, year = parts[:3]
            print(f" Parts: day={day}, month={month}, year={year}")
            
            # German to English month mapping with variations
            german_to_english = {
                # Standard German months
                'januar': 'January',
                'februar': 'February',
                'märz': 'March',
                'marz': 'March',
                'maerz': 'March',
                'april': 'April',
                'mai': 'May',
                'juni': 'June',
                'juli': 'July',
                'august': 'August',
                'september': 'September',
                'oktober': 'October',
                'november': 'November',
                'dezember': 'December',
                
                # Common abbreviations and variations
                'jan': 'January',
                'feb': 'February',
                'mar': 'March',
                'apr': 'April',
                'jun': 'June',
                'jul': 'July',
                'aug': 'August',
                'sep': 'September',
                'okt': 'October',
                'nov': 'November',
                'dez': 'December'
            }
            
            # Normalize and clean month name
            month = month.strip().lower()
            print(f" Normalized month: {month}")
            
            # Try direct lookup first
            if month not in german_to_english:
                # Try with normalized characters
                month_norm = ''.join(c for c in unicodedata.normalize('NFKD', month) if not unicodedata.combining(c))
                print(f" Normalized month (no diacritics): {month_norm}")
                if month_norm in german_to_english:
                    month = month_norm
            
            if month in german_to_english:
                month = german_to_english[month]
                print(f" Converted month: {month}")
            else:
                print(f" Unknown month: {month}")
                # Try to find closest match
                for german_month in german_to_english.keys():
                    if german_month.startswith(month[:2]):
                        print(f" Found potential match: {german_month}")
                return None
            
            # Ensure day is two digits
            day = f"{int(day):02d}"
            
            # Parse the date
            formatted_date = f"{day} {month} {year}"
            print(f" Attempting to parse: {formatted_date}")
            try:
                dt = datetime.strptime(formatted_date, "%d %B %Y")
                print(f" Successfully parsed date: {formatted_date}")
                return dt
            except ValueError as e:
                print(f" Failed to parse: {formatted_date} ({str(e)})")
                return None
                
    except (ValueError, IndexError) as e:
        print(f" Failed to parse: {date_text} ({str(e)})")
        return None

def scrape_anthropic_news(weeks_back=None, scrape_until_known=False, limit_by_posts=False, post_limit=None, page=None) -> List[Dict]:
    """
    Scrape Anthropic news articles with configurable limits and options.
    Now loads the listing page URL from web_sources.json and discovers article links dynamically.
    
    The scraping process:
    1. Initializes a headless browser with human-like settings
    2. Visits the Anthropic news page
    3. Attempts to find articles using multiple selector strategies
    4. For each article:
       - Extracts title and content
       - Parses publication date
       - Cleans and formats content
       - Checks for duplicates
       - Applies age limits if specified
    5. Returns a list of processed articles
    
    Args:
        weeks_back (int, optional): Number of weeks into the past to scrape
        scrape_until_known (bool): Stop when finding a known article
        limit_by_posts (bool): Whether to limit by number of posts
        post_limit (int): How many posts to scrape (if limit_by_posts=True)
        page: Optional Playwright page object for dependency injection (for testing)
    
    Returns:
        List[Dict]: List of processed articles with the following structure:
            {
                "source": "Anthropic",
                "platform": "Website",
                "url": str,
                "content": str,
                "summary": Optional[str],
                "timestamp": str (ISO format)
            }
    """
    posts = []
    cutoff_date = None
    if weeks_back is not None:
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks_back)

    # Load the listing page URL from web_sources.json
    with open(os.path.join(os.path.dirname(__file__), '../web_sources.json'), 'r', encoding='utf-8') as f:
        listing_urls = json.load(f)
    if not listing_urls:
        print("No listing URLs found in web_sources.json")
        return posts
    listing_url = listing_urls[0]

    print(f" Starting Anthropic news scraper using listing page: {listing_url}")

    # If no page is provided, create one using Playwright
    if page is None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

    try:
        # Visit the listing page
        print(f" Visiting listing page: {listing_url}")
        page.goto(listing_url, wait_until="networkidle")

        # Try multiple possible selectors for news links
        selectors = [
            "a[data-testid='link-card']",
            "a[href*='/news/']",
            "main a[href]",
            "[role='article'] a"
        ]

        article_links = []
        for selector in selectors:
            try:
                print(f" Trying to find articles with selector: {selector}")
                page.wait_for_selector(selector, timeout=5000)
                links = page.query_selector_all(selector)
                if links:
                    if limit_by_posts and post_limit is not None:
                        article_links = links[:post_limit]
                        print(f" Limited to {post_limit} articles using selector: {selector}")
                    else:
                        article_links = links
                        print(f" Found {len(links)} articles using selector: {selector}")
                    break
            except TimeoutError:
                continue

        if not article_links:
            raise Exception("Could not find any news articles with known selectors")

        # Extract hrefs before navigating away
        article_urls = []
        for link in article_links:
            try:
                href = link.get_attribute("href")
                if href and ("/news/" in href or "/blog/" in href):
                    article_urls.append(href)
            except Exception:
                continue

        print(f" Found {len(article_urls)} valid article URLs")

        posts_scraped = 0
        for url in article_urls:
            try:
                full_url = url if url.startswith("http") else f"https://www.anthropic.com{url}"
                
                # Check if URL exists and we're in scrape_until_known mode
                if scrape_until_known and url_exists(full_url):
                    print(f" Found known article: {full_url}")
                    print(" Stopping scrape as requested")
                    break
                
                print(f" Processing article: {full_url}")
                
                page.goto(full_url, wait_until="networkidle")
                
                # Try multiple selectors for title
                title_text = ""
                for title_selector in ["h1", "[role='heading']", "main h1"]:
                    title = page.query_selector(title_selector)
                    if title:
                        title_text = title.inner_text().strip()
                        break

                # Get published date from div after title
                published_date = None
                date_text = None
                date_el = page.query_selector("h1 + div")
                if date_el:
                    date_text = date_el.inner_text().strip()
                    if '●' in date_text:
                        date_text_for_parse = date_text.split('●')[0].strip()  # e.g., "24. Feb. 2025"
                        parsed_date = parse_text_date(date_text_for_parse)
                        if parsed_date:
                            published_date = parsed_date.isoformat()
                            print(f" Found publication date: {published_date}")
                        else:
                            print(f" Failed to parse date: {date_text_for_parse}")

                # Get content from article element
                content_text = ""
                article = page.query_selector("article")
                if article:
                    content_text = article.inner_text().strip()
                    # Remove duplicate title if it appears at the start
                    if title_text and content_text.startswith(title_text):
                        content_text = content_text[len(title_text):].strip()
                    # Remove date_text if it appears at the start
                    if date_text and content_text.startswith(date_text):
                        content_text = content_text[len(date_text):].strip()
                    # Remove duplicate URL if it appears at the start
                    if content_text.startswith(full_url):
                        content_text = content_text[len(full_url):].strip()
                    # Remove metadata lines (e.g., "Announcements", "5 min read", etc.)
                    lines = content_text.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        # Skip empty lines and metadata
                        if not line or line in ['Announcements', 'Product', 'Policy', 'Societal Impacts']:
                            continue
                        # Skip lines with read time
                        if '●' in line and ('min read' in line or 'read' in line):
                            continue
                        # Skip duplicate title
                        if title_text and line == title_text:
                            continue
                        cleaned_lines.append(line)
                    content_text = ' '.join(cleaned_lines)
                
                # Fallback to current time if no date found
                if not published_date:
                    published_date = datetime.utcnow().isoformat()
                    print(" Could not find article date, using current time")
                
                # Check if article is too old
                if cutoff_date is not None:
                    try:
                        article_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                        if article_date < cutoff_date:
                            print(f" Article from {article_date} is older than cutoff {cutoff_date}")
                            print(" Stopping scrape due to age")
                            break
                    except ValueError:
                        # If we can't parse the date, continue but warn
                        print(f" Could not parse article date: {published_date}")
                
                # Extract thumbnail
                thumbnail = None

                # Try to get the first image in the article
                img_tag = page.query_selector("article img")
                if img_tag:
                    thumbnail = img_tag.get_attribute("src")
                    thumbnail = clean_thumbnail_url(thumbnail)

                # Fallback: check for og:image meta tag
                if not thumbnail:
                    og_image = page.query_selector("meta[property='og:image']")
                    if og_image:
                        thumbnail = og_image.get_attribute("content")
                        thumbnail = clean_thumbnail_url(thumbnail)

                # Final fallback: placeholder
                if not thumbnail:
                    thumbnail = 'https://placehold.co/64x64?text=No+Image'
                
                # Extract author
                author = None

                # Try common selectors for author in the article
                author_selectors = [
                    "article [class*='author']",
                    "article .byline",
                    "article [rel='author']"
                ]
                for selector in author_selectors:
                    author_el = page.query_selector(selector)
                    if author_el:
                        author = author_el.inner_text().strip()
                        break

                # Fallback: meta tag in head
                if not author:
                    meta_author = page.query_selector("meta[name='author']")
                    if meta_author:
                        author = meta_author.get_attribute("content")

                # If still not found, leave as None
                
                if title_text and content_text:
                    post = {
                        "source": "Anthropic",
                        "platform": "Website",
                        "url": full_url,
                        "title": title_text,
                        "content": content_text,
                        "summary": None,
                        "timestamp": published_date,
                        "thumbnail": thumbnail,
                        "author": author
                    }
                    posts.append(post)
                    posts_scraped += 1
                    print(f" Captured article: {title_text}")

                    # Check if we've reached the post limit
                    if limit_by_posts and post_limit is not None and posts_scraped >= post_limit:
                        print(f" Reached post limit of {post_limit}. Stopping.")
                        break
                
            except Exception as e:
                print(f" Error processing article: {str(e)}")
                continue
            
    except Exception as e:
        print(f" Error during scraping: {str(e)}")
    finally:
        if page is None:
            browser.close()
    
    # Deduplicate posts by URL before returning
    unique_posts = {}
    for post in posts:
        if post['url'] not in unique_posts:
            unique_posts[post['url']] = post
    return list(unique_posts.values())

def normalize_url(url: str) -> str:
    """
    Normalize URL to ensure consistent comparison for duplicate detection.
    - Removes trailing slashes
    - Converts to lowercase
    - Removes common tracking parameters
    """
    if not url:
        return url
    
    # Convert to lowercase and remove trailing slash
    url = url.lower().rstrip('/')
    
    # Remove common tracking parameters
    tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
    if '?' in url:
        base, params = url.split('?', 1)
        param_dict = dict(param.split('=') for param in params.split('&') if '=' in param)
        filtered_params = {k: v for k, v in param_dict.items() if k not in tracking_params}
        if filtered_params:
            url = f"{base}?{'&'.join(f'{k}={v}' for k, v in filtered_params.items())}"
        else:
            url = base
    
    return url

def save_posts_to_db(posts: list):
    """
    Save posts to the database, avoiding duplicates by URL.
    Each post is checked for uniqueness by its URL. If a post with the same URL does not exist,
    it is added to the database. Errors for individual posts are logged and do not stop the batch.
    If the commit fails, the transaction is rolled back and the error is raised.

    Args:
        posts (list): List of post dictionaries to save

    Returns:
        int: Number of new posts saved to the database
    """
    db = SessionLocal()
    new_posts = 0
    duplicate_count = 0
    error_count = 0
    
    try:
        # Start a transaction
        with db.begin():
            # Normalize URLs and create a set for faster lookup
            existing_urls = {
                normalize_url(post.url) 
                for post in db.query(Post.url).all()
            }
            
            for post in posts:
                try:
                    # Normalize the URL for comparison
                    normalized_url = normalize_url(post['url'])
                    
                    # Skip if URL is None or empty
                    if not normalized_url:
                        logging.warning(f"Skipping post with empty URL: {post.get('title', 'Unknown')}")
                        continue
                    
                    # Check for duplicates using normalized URL
                    if normalized_url in existing_urls:
                        duplicate_count += 1
                        logging.info(f"Duplicate post skipped: {post['title']} ({post['url']})")
                        continue
                    
                    # Ensure timestamp is a datetime object
                    timestamp = post['timestamp']
                    if isinstance(timestamp, str):
                        try:
                            # Remove 'Z' if present and parse
                            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except Exception:
                            timestamp = datetime.utcnow()
                    
                    # Create new post
                    db_post = Post(
                        source=post['source'],
                        platform=post['platform'],
                        url=post['url'],  # Store original URL
                        title=post['title'],
                        content=post['content'],
                        summary=post.get('summary'),
                        timestamp=timestamp,
                        thumbnail=post.get('thumbnail'),
                        author=post.get('author'),
                    )
                    db.add(db_post)
                    new_posts += 1
                    existing_urls.add(normalized_url)  # Add to set for subsequent checks
                    logging.info(f"Added new post: {post['title']} ({post['url']})")
                    
                except Exception as e:
                    error_count += 1
                    logging.error(f"Error saving post {post.get('url')}: {str(e)}")
                    continue
            
            # Log summary
            logging.info(
                f"Database update complete. "
                f"New posts: {new_posts}, "
                f"Duplicates skipped: {duplicate_count}, "
                f"Errors: {error_count} "
                f"(out of {len(posts)} total posts)"
            )
            
    except Exception as e:
        logging.error(f"Transaction failed: {str(e)}")
        raise
    finally:
        db.close()
    
    return new_posts

def clean_thumbnail_url(url, base="https://www.anthropic.com"):
    if not url:
        return None
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return base.rstrip("/") + url
    return base.rstrip("/") + "/" + url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Anthropic news scraper and save to DB.")
    parser.add_argument('--post-limit', type=int, default=None, help='Number of articles to scrape (default: all)')
    args = parser.parse_args()

    print("Running Anthropic scraper and saving to DB...")
    if args.post_limit is not None:
        posts = scrape_anthropic_news(limit_by_posts=True, post_limit=args.post_limit)
    else:
        posts = scrape_anthropic_news()
    if posts:
        print(f"Scraped {len(posts)} posts. Saving to database...")
        saved = save_posts_to_db(posts)
        print(f"Saved {saved} new posts to the database.")
    else:
        print("No posts found.") 