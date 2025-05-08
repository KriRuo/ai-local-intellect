import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from ..db.models import Post
from sqlalchemy.orm import Session
import logging

class SubstackScraperError(Exception):
    pass

def scrape_substack_articles(url: str) -> List[Dict]:
    """
    Scrape articles from a Substack archive page
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        # Find all article elements
        for article in soup.find_all('article'):
            try:
                # Extract article data
                title_elem = article.find('h2')
                link_elem = article.find('a')
                time_elem = article.find('time')
                author_elem = article.find(class_='author')
                summary_elem = article.find(class_='description')
                img_elem = article.find('img')

                if not title_elem or not link_elem:
                    continue

                article_data = {
                    'title': title_elem.text.strip(),
                    'url': link_elem.get('href', ''),
                    'publishedDate': time_elem.text.strip() if time_elem else None,
                    'author': author_elem.text.strip() if author_elem else None,
                    'summary': summary_elem.text.strip() if summary_elem else None,
                    'thumbnail': img_elem.get('src') if img_elem else None,
                    'source': 'Substack',
                    'platform': 'Substack'
                }
                articles.append(article_data)
            except Exception as e:
                logging.warning(f"Error parsing article: {e}")
                continue

        return articles
    except Exception as e:
        raise SubstackScraperError(f"Failed to scrape Substack: {str(e)}")

def save_substack_articles(db: Session, articles: List[Dict]) -> List[Post]:
    """
    Save scraped Substack articles to the database
    """
    saved_posts = []
    for article in articles:
        try:
            # Check if post already exists
            existing_post = db.query(Post).filter(Post.url == article['url']).first()
            if existing_post:
                continue

            # Create new post
            post = Post(
                source=article['source'],
                platform=article['platform'],
                url=article['url'],
                title=article['title'],
                content=article['summary'],  # Using summary as content
                summary=article['summary'],
                timestamp=datetime.fromisoformat(article['publishedDate']) if article['publishedDate'] else None,
                thumbnail=article['thumbnail'],
                author=article['author']
            )
            db.add(post)
            saved_posts.append(post)
        except Exception as e:
            logging.warning(f"Error saving article {article.get('url')}: {e}")
            continue

    db.commit()
    return saved_posts

def scrape_and_save_substack(db: Session, url: str) -> List[Post]:
    """
    Scrape Substack articles and save them to the database
    """
    articles = scrape_substack_articles(url)
    return save_substack_articles(db, articles) 