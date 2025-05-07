"""
RSS Feed Scraper Module

This module provides functionality to scrape RSS feeds from various sources.
It uses the feedparser library to parse RSS/Atom feeds and includes error handling
and content cleaning.
"""

import feedparser
from datetime import datetime
from typing import List, Dict
from time import mktime
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..db.models import Post
import logging

def clean_content(content: str) -> str:
    """
    Clean HTML content from RSS feed.
    
    Args:
        content (str): Raw content from RSS feed
        
    Returns:
        str: Cleaned content with HTML removed
    """
    # For now, just return the raw content
    # TODO: Add HTML cleaning if needed
    return content.strip()

def scrape_rss_feed(url: str, source: str, platform: str = "RSS") -> List[Dict]:
    """
    Scrape posts from an RSS feed.
    
    Args:
        url (str): The RSS feed URL
        source (str): Name of the source organization
        platform (str): Platform name (defaults to "RSS")
        
    Returns:
        List[Dict]: List of processed posts
    """
    posts = []
    print(f"📡 Fetching RSS feed from {url}...")
    
    # Parse the feed
    feed = feedparser.parse(url)
    
    if feed.bozo:
        raise Exception(f"Error parsing feed: {feed.bozo_exception}")
    
    # Process each entry
    for entry in feed.entries:
        try:
            # Get the URL
            post_url = entry.link
            
            # Get content (prefer content over summary if available)
            content = ""
            if hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description
                
            if not content:
                print(f"⚠️ No content found for {post_url}")
                continue
                
            # Clean content
            content = clean_content(content)
            
            # Get timestamp
            if hasattr(entry, "published_parsed"):
                timestamp = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat()
            elif hasattr(entry, "updated_parsed"):
                timestamp = datetime.fromtimestamp(mktime(entry.updated_parsed)).isoformat()
            else:
                timestamp = datetime.utcnow().isoformat()
                print("⚠️ No timestamp found, using current time")
            
            # Extract thumbnail
            thumbnail = None
            if hasattr(entry, "media_content") and entry.media_content:
                for media in entry.media_content:
                    if hasattr(media, "url"):
                        thumbnail = media.url
                        break
            elif hasattr(entry, "image") and entry.image:
                thumbnail = entry.image.href
            elif hasattr(entry, "links"):
                for link in entry.links:
                    if link.get("type", "").startswith("image/"):
                        thumbnail = link.get("href")
                        break
            # Fallback: extract first image from content if no thumbnail found
            if not thumbnail:
                soup = BeautifulSoup(content, 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    thumbnail = img_tag['src']
            # Final fallback: always set placeholder if still no thumbnail
            if not thumbnail:
                thumbnail = 'https://placehold.co/64x64?text=No+Image'
            
            # Extract author
            author = getattr(entry, 'author', None)
            if not author and hasattr(entry, 'authors') and entry.authors:
                author = entry.authors[0].get('name', None)
            
            # Create post object
            post = {
                "source": source,
                "platform": platform,
                "url": post_url,
                "title": getattr(entry, 'title', None),
                "content": content,
                "summary": None,
                "timestamp": timestamp,
                "thumbnail": thumbnail,
                "author": author
            }
            
            posts.append(post)
            print(f"✅ Captured: {entry.title}")
            
        except Exception as e:
            print(f"⚠️ Error processing entry: {str(e)}")
            continue
    
    return posts 

def save_posts_to_db(db: Session, posts: list):
    """Save posts to the database, avoiding duplicates by URL."""
    new_posts = 0
    for post in posts:
        if not db.query(Post).filter_by(url=post['url']).first():
            db_post = Post(
                source=post['source'],
                platform=post['platform'],
                url=post['url'],
                title=post['title'],
                content=post['content'],
                summary=post.get('summary'),
                timestamp=post['timestamp'],
                thumbnail=post.get('thumbnail'),
                author=post.get('author'),
            )
            db.add(db_post)
            new_posts += 1
    db.commit()
    logging.info(f"Saved {new_posts} new posts to the database (out of {len(posts)} scraped).");

# Utility to scrape and save in one go

def scrape_and_save_rss_feed(db: Session, url: str, source: str, platform: str = "RSS"):
    posts = scrape_rss_feed(url, source, platform)
    save_posts_to_db(db, posts)
    return posts 