from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..db.models import RssScrapeRun, Post, PipelineFailure
import logging

class PipelineLogger:
    def __init__(self, db: Session):
        self.db = db
        self.current_run: Optional[RssScrapeRun] = None
        self.stats = {
            'total_items': 0,
            'successful_items': 0,
            'failed_items': 0,
            'skipped_items': 0
        }

    def start_run(self, source: str, run_type: str = 'rss_scrape') -> RssScrapeRun:
        """Start a new pipeline run and return the run object"""
        logger = logging.getLogger(__name__)
        logger.info(f"[PipelineLogger] About to create RssScrapeRun: source={source}, run_type={run_type}")
        try:
            self.current_run = RssScrapeRun(
                started_at=datetime.utcnow(),
                source=source,
                run_type=run_type,
                status="running"
            )
            logger.info(f"[PipelineLogger] Created RssScrapeRun object (not committed yet)")
            self.db.add(self.current_run)
            logger.info(f"[PipelineLogger] Added RssScrapeRun to session")
            self.db.commit()
            logger.info(f"[PipelineLogger] Committed RssScrapeRun to DB")
            self.db.refresh(self.current_run)
            logger.info(f"[PipelineLogger] Refreshed RssScrapeRun from DB: id={self.current_run.id}")
            return self.current_run
        except Exception as e:
            logger.error(f"[PipelineLogger] Exception in start_run: {e}", exc_info=True)
            raise

    def log_article_processed(self, article: Dict[str, Any], status: str, stage: str, error_message: Optional[str] = None):
        """Log the processing of a single article at a specific stage"""
        self.stats['total_items'] += 1
        
        if status == 'success':
            self.stats['successful_items'] += 1
        elif status == 'error':
            self.stats['failed_items'] += 1
            if error_message:
                failure = PipelineFailure(
                    run_id=self.current_run.id,
                    article_url=article.get('url'),
                    stage=stage,
                    error_message=error_message,
                    occurred_at=datetime.utcnow()
                )
                self.db.add(failure)
        elif status == 'skipped':
            self.stats['skipped_items'] += 1

    def end_run(self, status: str = 'completed', error_message: Optional[str] = None):
        """End the current pipeline run and update statistics"""
        if not self.current_run:
            return

        self.current_run.ended_at = datetime.utcnow()
        self.current_run.duration_seconds = (self.current_run.ended_at - self.current_run.started_at).total_seconds()
        self.current_run.status = status
        self.current_run.error_message = error_message
        self.current_run.num_sources_total = self.stats['total_items']
        self.current_run.num_sources_captured = self.stats['successful_items']
        self.current_run.num_sources_skipped = self.stats['skipped_items'] + self.stats['failed_items']
        
        self.db.commit()
        self.print_summary()

    def print_summary(self):
        """Print a human-readable summary of the pipeline run"""
        if not self.current_run:
            return

        print("\n----- Pipeline Summary -----")
        print(f"Source       : {self.current_run.source}")
        print(f"Run Type     : {self.current_run.run_type}")
        print(f"Status       : {self.current_run.status}")
        print(f"Duration     : {self.current_run.duration_seconds:.2f} seconds")
        print(f"Total Items  : {self.stats['total_items']}")
        print(f"Successful   : {self.stats['successful_items']}")
        print(f"Failed       : {self.stats['failed_items']}")
        print(f"Skipped      : {self.stats['skipped_items']}")
        print("-----------------------------\n") 