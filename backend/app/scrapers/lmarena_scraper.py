"""
Lmarena Blog Scraper Module

This module provides functionality to scrape blog articles from Lmarena's website.
It is based on the Anthropic scraper template and will be customized for Lmarena's structure.
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
    print(f" Attempting to parse date: {date_text}")
    date_text = date_text.strip()
    print(f" Input text: {date_text}")
    try:
        parts = [p.strip() for p in date_text.split('.') if p.strip()]
        print(f" Initial split parts: {parts}")
        if len(parts) == 2 and ' ' in parts[1]:
            month_year = parts[1].split()
            if len(month_year) == 2:
                parts = [parts[0], month_year[0], month_year[1]]
        print(f" Processed parts: {parts}")
        if len(parts) >= 3:
            day, month, year = parts[:3]
            print(f" Parts: day={day}, month={month}, year={year}")
            german_to_english = {
                'januar': 'January', 'februar': 'February', 'märz': 'March', 'marz': 'March', 'maerz': 'March',
                'april': 'April', 'mai': 'May', 'juni': 'June', 'juli': 'July', 'august': 'August',
                'september': 'September', 'oktober': 'October', 'november': 'November', 'dezember': 'December',
                'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April', 'jun': 'June', 'jul': 'July',
                'aug': 'August', 'sep': 'September', 'okt': 'October', 'nov': 'November', 'dez': 'December'
            }
            month = month.strip().lower()
            print(f" Normalized month: {month}")
            if month not in german_to_english:
                month_norm = ''.join(c for c in unicodedata.normalize('NFKD', month) if not unicodedata.combining(c))
                print(f" Normalized month (no diacritics): {month_norm}")
                if month_norm in german_to_english:
                    month = month_norm
            if month in german_to_english:
                month = german_to_english[month]
                print(f" Converted month: {month}")
            else:
                print(f" Unknown month: {month}")
                for german_month in german_to_english.keys():
                    if german_month.startswith(month[:2]):
                        print(f" Found potential match: {german_month}")
                return None
            day = f"{int(day):02d}"
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

def scrape_lmarena_blog(weeks_back=None, scrape_until_known=False, limit_by_posts=False, post_limit=None, page=None) -> List[Dict]:
    posts = []
    cutoff_date = None
    if weeks_back is not None:
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks_back)
    with open(os.path.join(os.path.dirname(__file__), '../web_sources.json'), 'r', encoding='utf-8') as f:
        listing_urls = json.load(f)
    if not listing_urls:
        print("No listing URLs found in web_sources.json")
        return posts
    listing_url = listing_urls[1] if len(listing_urls) > 1 else listing_urls[0]
    print(f" Starting Lmarena blog scraper using listing page: {listing_url}")
    if page is None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            try:
                print(f" Visiting listing page: {listing_url}")
                page.goto(listing_url, wait_until="networkidle")
                selectors = [
                    "a[data-testid='link-card']",
                    "a[href*='/blog/']",
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
                    raise Exception("Could not find any blog articles with known selectors")
                article_urls = []
                for link in article_links:
                    try:
                        href = link.get_attribute("href")
                        if href and "/blog/" in href:
                            article_urls.append(href)
                    except Exception:
                        continue
                print(f" Found {len(article_urls)} valid article URLs")
                posts_scraped = 0
                for url in article_urls:
                    try:
                        full_url = url if url.startswith("http") else f"https://blog.lmarena.ai{url}"
                        if scrape_until_known and url_exists(full_url):
                            print(f" Found known article: {full_url}")
                            print(" Stopping scrape as requested")
                            break
                        print(f" Processing article: {full_url}")
                        page.goto(full_url, wait_until="networkidle")
                        title_text = ""
                        for title_selector in ["h1", "[role='heading']", "main h1"]:
                            title = page.query_selector(title_selector)
                            if title:
                                title_text = title.inner_text().strip()
                                break
                        published_date = None
                        date_text = None

                        # --- Updated date extraction logic ---
                        # Find the <h3>Published</h3> and its following <p>
                        date_el = None
                        for h3 in page.query_selector_all(".byline.grid h3"):
                            if h3.inner_text().strip().lower() == "published":
                                # Get the next sibling <p>
                                p = h3.evaluate_handle("node => node.nextElementSibling")
                                if p:
                                    date_text = p.inner_text().strip()
                                    try:
                                        parsed_date = datetime.strptime(date_text, "%B %d, %Y")
                                        published_date = parsed_date.isoformat()
                                        print(f" Found publication date: {published_date}")
                                    except ValueError:
                                        print(f" Failed to parse date: {date_text}")
                                break
                        # Fallback if not found
                        if not published_date:
                            published_date = datetime.utcnow().isoformat()
                            print(" Could not find article date, using current time")

                        # --- Updated author extraction logic ---
                        author = None
                        for h3 in page.query_selector_all(".byline.grid h3"):
                            if h3.inner_text().strip().lower() == "authors":
                                p = h3.evaluate_handle("node => node.nextElementSibling")
                                if p:
                                    span = p.query_selector("span.name")
                                    if span:
                                        author = span.inner_text().strip()
                                    else:
                                        author = p.inner_text().strip()
                                break
                        # Fallback: meta tag in head
                        if not author:
                            meta_author = page.query_selector("meta[name='author']")
                            if meta_author:
                                author = meta_author.get_attribute("content")
                        content_text = ""
                        article = page.query_selector("article")
                        if article:
                            content_text = article.inner_text().strip()
                            if title_text and content_text.startswith(title_text):
                                content_text = content_text[len(title_text):].strip()
                            if date_text and content_text.startswith(date_text):
                                content_text = content_text[len(date_text):].strip()
                            if content_text.startswith(full_url):
                                content_text = content_text[len(full_url):].strip()
                            lines = content_text.split('\n')
                            cleaned_lines = []
                            for line in lines:
                                line = line.strip()
                                if not line or line in ['Announcements', 'Product', 'Policy', 'Societal Impacts']:
                                    continue
                                if '●' in line and ('min read' in line or 'read' in line):
                                    continue
                                if title_text and line == title_text:
                                    continue
                                cleaned_lines.append(line)
                            content_text = ' '.join(cleaned_lines)
                        if not published_date:
                            published_date = datetime.utcnow().isoformat()
                            print(" Could not find article date, using current time")
                        if cutoff_date is not None:
                            try:
                                article_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                                if article_date < cutoff_date:
                                    print(f" Article from {article_date} is older than cutoff {cutoff_date}")
                                    print(" Stopping scrape due to age")
                                    break
                            except ValueError:
                                print(f" Could not parse article date: {published_date}")
                        thumbnail = None
                        img_tag = page.query_selector("article img")
                        if img_tag:
                            thumbnail = img_tag.get_attribute("src")
                            thumbnail = clean_thumbnail_url(thumbnail)
                        if not thumbnail:
                            og_image = page.query_selector("meta[property='og:image']")
                            if og_image:
                                thumbnail = og_image.get_attribute("content")
                                thumbnail = clean_thumbnail_url(thumbnail)
                        if not thumbnail:
                            thumbnail = 'https://placehold.co/64x64?text=No+Image'
                        if title_text and content_text:
                            post = {
                                "source": "Lmarena",
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
                            if limit_by_posts and post_limit is not None and posts_scraped >= post_limit:
                                print(f" Reached post limit of {post_limit}. Stopping.")
                                break
                    except Exception as e:
                        print(f" Error processing article: {str(e)}")
                        continue
            except Exception as e:
                print(f" Error during scraping: {str(e)}")
            finally:
                browser.close()
    else:
        # If page is provided (for testing), use it directly
        try:
            print(f" Visiting listing page: {listing_url}")
            page.goto(listing_url, wait_until="networkidle")
            selectors = [
                "a[data-testid='link-card']",
                "a[href*='/blog/']",
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
                raise Exception("Could not find any blog articles with known selectors")
            article_urls = []
            for link in article_links:
                try:
                    href = link.get_attribute("href")
                    if href and "/blog/" in href:
                        article_urls.append(href)
                except Exception:
                    continue
            print(f" Found {len(article_urls)} valid article URLs")
            posts_scraped = 0
            for url in article_urls:
                try:
                    full_url = url if url.startswith("http") else f"https://blog.lmarena.ai{url}"
                    if scrape_until_known and url_exists(full_url):
                        print(f" Found known article: {full_url}")
                        print(" Stopping scrape as requested")
                        break
                    print(f" Processing article: {full_url}")
                    page.goto(full_url, wait_until="networkidle")
                    title_text = ""
                    for title_selector in ["h1", "[role='heading']", "main h1"]:
                        title = page.query_selector(title_selector)
                        if title:
                            title_text = title.inner_text().strip()
                            break
                    published_date = None
                    date_text = None

                    # --- Updated date extraction logic ---
                    # Find the <h3>Published</h3> and its following <p>
                    date_el = None
                    for h3 in page.query_selector_all(".byline.grid h3"):
                        if h3.inner_text().strip().lower() == "published":
                            # Get the next sibling <p>
                            p = h3.evaluate_handle("node => node.nextElementSibling")
                            if p:
                                date_text = p.inner_text().strip()
                                try:
                                    parsed_date = datetime.strptime(date_text, "%B %d, %Y")
                                    published_date = parsed_date.isoformat()
                                    print(f" Found publication date: {published_date}")
                                except ValueError:
                                    print(f" Failed to parse date: {date_text}")
                            break
                    # Fallback if not found
                    if not published_date:
                        published_date = datetime.utcnow().isoformat()
                        print(" Could not find article date, using current time")

                    # --- Updated author extraction logic ---
                    author = None
                    for h3 in page.query_selector_all(".byline.grid h3"):
                        if h3.inner_text().strip().lower() == "authors":
                            p = h3.evaluate_handle("node => node.nextElementSibling")
                            if p:
                                span = p.query_selector("span.name")
                                if span:
                                    author = span.inner_text().strip()
                                else:
                                    author = p.inner_text().strip()
                            break
                    # Fallback: meta tag in head
                    if not author:
                        meta_author = page.query_selector("meta[name='author']")
                        if meta_author:
                            author = meta_author.get_attribute("content")
                    content_text = ""
                    article = page.query_selector("article")
                    if article:
                        content_text = article.inner_text().strip()
                        if title_text and content_text.startswith(title_text):
                            content_text = content_text[len(title_text):].strip()
                        if date_text and content_text.startswith(date_text):
                            content_text = content_text[len(date_text):].strip()
                        if content_text.startswith(full_url):
                            content_text = content_text[len(full_url):].strip()
                        lines = content_text.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            line = line.strip()
                            if not line or line in ['Announcements', 'Product', 'Policy', 'Societal Impacts']:
                                continue
                            if '●' in line and ('min read' in line or 'read' in line):
                                continue
                            if title_text and line == title_text:
                                continue
                            cleaned_lines.append(line)
                        content_text = ' '.join(cleaned_lines)
                    if not published_date:
                        published_date = datetime.utcnow().isoformat()
                        print(" Could not find article date, using current time")
                    if cutoff_date is not None:
                        try:
                            article_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                            if article_date < cutoff_date:
                                print(f" Article from {article_date} is older than cutoff {cutoff_date}")
                                print(" Stopping scrape due to age")
                                break
                        except ValueError:
                            print(f" Could not parse article date: {published_date}")
                    thumbnail = None
                    img_tag = page.query_selector("article img")
                    if img_tag:
                        thumbnail = img_tag.get_attribute("src")
                        thumbnail = clean_thumbnail_url(thumbnail)
                    if not thumbnail:
                        og_image = page.query_selector("meta[property='og:image']")
                        if og_image:
                            thumbnail = og_image.get_attribute("content")
                            thumbnail = clean_thumbnail_url(thumbnail)
                    if not thumbnail:
                        thumbnail = 'https://placehold.co/64x64?text=No+Image'
                    if title_text and content_text:
                        post = {
                            "source": "Lmarena",
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
                        if limit_by_posts and post_limit is not None and posts_scraped >= post_limit:
                            print(f" Reached post limit of {post_limit}. Stopping.")
                            break
                except Exception as e:
                    print(f" Error processing article: {str(e)}")
                    continue
        except Exception as e:
            print(f" Error during scraping: {str(e)}")
    unique_posts = {}
    for post in posts:
        if post['url'] not in unique_posts:
            unique_posts[post['url']] = post
    return list(unique_posts.values())

def normalize_url(url: str) -> str:
    if not url:
        return url
    url = url.lower().rstrip('/')
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
    db = SessionLocal()
    new_posts = 0
    duplicate_count = 0
    error_count = 0
    try:
        with db.begin():
            existing_urls = {
                normalize_url(post.url) 
                for post in db.query(Post.url).all()
            }
            for post in posts:
                try:
                    normalized_url = normalize_url(post['url'])
                    if not normalized_url:
                        logging.warning(f"Skipping post with empty URL: {post.get('title', 'Unknown')}")
                        continue
                    if normalized_url in existing_urls:
                        duplicate_count += 1
                        logging.info(f"Duplicate post skipped: {post['title']} ({post['url']})")
                        continue
                    timestamp = post['timestamp']
                    if isinstance(timestamp, str):
                        try:
                            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except Exception:
                            timestamp = datetime.utcnow()
                    db_post = Post(
                        source=post['source'],
                        platform=post['platform'],
                        url=post['url'],
                        title=post['title'],
                        content=post['content'],
                        summary=post.get('summary'),
                        timestamp=timestamp,
                        thumbnail=post.get('thumbnail'),
                        author=post.get('author'),
                    )
                    db.add(db_post)
                    new_posts += 1
                    existing_urls.add(normalized_url)
                    logging.info(f"Added new post: {post['title']} ({post['url']})")
                except Exception as e:
                    error_count += 1
                    logging.error(f"Error saving post {post.get('url')}: {str(e)}")
                    continue
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

def clean_thumbnail_url(url, base="https://blog.lmarena.ai"):
    if not url:
        return None
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return base.rstrip("/") + url
    return base.rstrip("/") + "/" + url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Lmarena blog scraper and save to DB.")
    parser.add_argument('--post-limit', type=int, default=None, help='Number of articles to scrape (default: all)')
    args = parser.parse_args()
    print("Running Lmarena scraper and saving to DB...")
    if args.post_limit is not None:
        posts = scrape_lmarena_blog(limit_by_posts=True, post_limit=args.post_limit)
    else:
        posts = scrape_lmarena_blog()
    if posts:
        print(f"Scraped {len(posts)} posts. Saving to database...")
        saved = save_posts_to_db(posts)
        print(f"Saved {saved} new posts to the database.")
    else:
        print("No posts found.") 