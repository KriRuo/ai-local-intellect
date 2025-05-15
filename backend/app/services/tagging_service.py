import os
import json
import requests
from typing import Tuple, List, Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from ..db.models import Post
import logging
from openai import OpenAI
import re
from ..utils.tagging_logger import TaggingLogger

load_dotenv()

class TaggingService:
    def __init__(self):
        self.api_key = os.getenv("ChatGPT_API_KEY") or os.getenv("VITE_ChatGPT_API_KEY")
        self.org_id = os.getenv("OPENAI_ORG_ID")  # Optional
        self.project_id = os.getenv("OPENAI_PROJECT_ID")  # Optional
        if not self.api_key:
            raise ValueError("ChatGPT_API_KEY or VITE_ChatGPT_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=self.api_key,
            organization=self.org_id,
            project=self.project_id
        )
        self.model = "qwen/qwen3-0.6b-04-28:free"  # Kept for reference, not used for HF
        
    def get_tags_and_category(self, text: str):
        system_prompt = """
        You are an expert content classifier and keyword extractor focused on AI-related content.
        Given a text snippet, return:
        1. A list of 5–10 descriptive tags (keywords or phrases relevant to the text).
        2. The main category this text belongs to, chosen from the following AI-focused taxonomy:
           - Artificial General Intelligence (AGI)
           - Large Language Models (LLMs)
           - Natural Language Processing (NLP)
           - Computer Vision
           - Reinforcement Learning
           - Robotics
           - AI Ethics & Safety
           - AI Research
           - AI Applications (e.g. healthcare, finance, education)
           - AI Infrastructure & Tooling (e.g. GPUs, frameworks, APIs)
           - AI Policy & Regulation
           - AI Startups & Business
           - Multimodal AI
           - Open-Source AI
           - Other
        Return the result in JSON format:
        {
          "tags": [...],
          "category": "..."
        }
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=500
            )
            print("RAW OPENAI RESPONSE:", response)
            content = response.choices[0].message.content
            # Remove markdown code block if present
            content = re.sub(r'^```json\s*|^```\s*|```$', '', content.strip(), flags=re.MULTILINE)
            parsed = json.loads(content)
            return parsed.get("tags", []), parsed.get("category", "Other")
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {str(e)}")
            return [], "Other"

    def tag_new_posts(self, db: Session, batch_size: int = 3, status_filter: str = "pending") -> dict:
        """
        Tag posts in the database based on their tag_status.
        Args:
            db (Session): SQLAlchemy database session
            batch_size (int): Number of posts to process
            status_filter (str): Filter posts by tag_status ("pending" or "error")
        Returns:
            dict: Statistics about the tagging process
        """
        logger = TaggingLogger()
        try:
            # Get posts based on status filter
            new_posts = db.query(Post).filter(Post.tag_status == status_filter).order_by(Post.created_at.desc()).limit(batch_size).all()

            for post in new_posts:
                try:
                    tags, category = self.get_tags_and_category(post.content)
                    post.set_tags(tags)
                    post.category = category
                    post.tag_status = "tagged"
                    logger.log_processed(status="success")
                    logging.info(f"Tagged post {post.id}: {tags}, {category}")
                except Exception as e:
                    error_msg = str(e)
                    post.tag_status = "error"
                    logger.log_processed(status="error", error_message=error_msg)
                    logging.error(f"Error tagging post {post.id}: {error_msg}")

            db.commit()
            logger.print_summary()
            return logger.stats

        except Exception as e:
            error_msg = str(e)
            logger.log_processed(status="error", error_message=error_msg)
            logger.print_summary()
            raise

    def retry_failed_tags(self, db: Session, batch_size: int = 3) -> dict:
        """
        Retry tagging for posts that previously failed.
        Args:
            db (Session): SQLAlchemy database session
            batch_size (int): Number of posts to process
        Returns:
            dict: Statistics about the retry process
        """
        return self.tag_new_posts(db, batch_size=batch_size, status_filter="error") 