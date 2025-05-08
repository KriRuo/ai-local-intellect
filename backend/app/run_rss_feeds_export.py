import os
import json
from backend.app.db.database import SessionLocal
from backend.app.db.models import Post
from sqlalchemy.orm import Session
from datetime import datetime

# Path to output JSON file
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_feeds.json')

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
    }

def export_posts_to_json():
    db: Session = SessionLocal()
    try:
        posts = db.query(Post).order_by(Post.timestamp.desc()).all()
        posts_data = [post_to_dict(p) for p in posts]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"posts": posts_data}, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(posts_data)} posts to {output_path}")
    finally:
        db.close()

if __name__ == "__main__":
    export_posts_to_json() 