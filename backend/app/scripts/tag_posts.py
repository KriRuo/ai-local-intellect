import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.database import SessionLocal
from app.services.tagging_service import TaggingService
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    tagging_service = TaggingService()
    
    try:
        while True:
            # Tag the last 3 untagged posts
            stats = tagging_service.tag_new_posts(db, batch_size=3)
            logger.info(f"Tagged batch: {stats}")
            
            if stats["total_processed"] == 0:
                logger.info("No untagged posts found")
                # Wait for 1 minute before checking again
                time.sleep(60)
            else:
                # If we found and processed posts, check again immediately
                continue
                
    except KeyboardInterrupt:
        logger.info("Tagging process interrupted by user")
    finally:
        db.close()

if __name__ == "__main__":
    main() 