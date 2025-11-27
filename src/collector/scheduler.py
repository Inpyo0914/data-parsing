"""
Scheduler for automating periodic data collection.

This module uses APScheduler to run the crawler at configured intervals.
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, Any, Dict, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .crawler import FinancialJuiceCrawler
from .exceptions import CrawlerException
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class CrawlScheduler:
    """
    Scheduler for periodic data collection.

    Uses APScheduler to run crawling jobs at specified intervals.
    Supports cron-style scheduling configuration.

    Example:
        >>> scheduler = CrawlScheduler()
        >>> scheduler.schedule("0 9,15,21 * * *")  # 9AM, 3PM, 9PM daily
        >>> scheduler.start()
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ):
        """
        Initialize scheduler.

        Args:
            config: Configuration object
            on_success: Callback function called with crawl results on success
            on_error: Callback function called with exception on error
        """
        self.config = config or get_config()
        self.scheduler = AsyncIOScheduler()
        self.on_success = on_success
        self.on_error = on_error
        self._running = False

        logger.info("Initialized CrawlScheduler")

    async def run_crawl_job(self) -> Dict[str, List[Dict]]:
        """
        Execute a single crawl job.

        This is the job function that gets called by the scheduler.

        Returns:
            Dictionary mapping category names to article lists

        Raises:
            CrawlerException: If crawling fails
        """
        job_start = datetime.now()
        logger.info(f"Starting scheduled crawl job at {job_start.isoformat()}")

        try:
            # Create and run crawler
            async with FinancialJuiceCrawler(self.config) as crawler:
                results = await crawler.crawl_all()

            # Calculate statistics
            total_articles = sum(len(articles) for articles in results.values())
            job_duration = (datetime.now() - job_start).total_seconds()

            logger.info(
                f"Crawl job completed: {total_articles} articles "
                f"in {job_duration:.2f}s"
            )

            # Call success callback if provided
            if self.on_success:
                try:
                    if asyncio.iscoroutinefunction(self.on_success):
                        await self.on_success(results)
                    else:
                        self.on_success(results)
                except Exception as e:
                    logger.error(f"Error in success callback: {e}")

            return results

        except Exception as e:
            logger.error(f"Crawl job failed: {e}")

            # Call error callback if provided
            if self.on_error:
                try:
                    if asyncio.iscoroutinefunction(self.on_error):
                        await self.on_error(e)
                    else:
                        self.on_error(e)
                except Exception as callback_error:
                    logger.error(f"Error in error callback: {callback_error}")

            raise CrawlerException(f"Scheduled crawl failed: {e}")

    def schedule(self, cron_expression: Optional[str] = None) -> None:
        """
        Schedule the crawl job with a cron expression.

        Args:
            cron_expression: Cron expression (e.g., "0 9,15,21 * * *")
                           If None, uses config value

        Example:
            >>> scheduler.schedule("0 */6 * * *")  # Every 6 hours
        """
        if cron_expression is None:
            cron_expression = self.config.get(
                "scheduler.cron_schedule",
                "0 9,15,21 * * *"
            )

        # Parse cron expression
        # Format: minute hour day month day_of_week
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron expression: {cron_expression}. "
                "Expected format: 'minute hour day month day_of_week'"
            )

        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )

        # Add job to scheduler
        self.scheduler.add_job(
            self.run_crawl_job,
            trigger=trigger,
            id="crawl_job",
            name="FinancialJuice Crawl Job",
            replace_existing=True,
        )

        logger.info(f"Scheduled crawl job with cron: {cron_expression}")

    def start(self, run_immediately: bool = False) -> None:
        """
        Start the scheduler.

        Args:
            run_immediately: If True, run the job immediately before starting scheduler
        """
        if self._running:
            logger.warning("Scheduler is already running")
            return

        if run_immediately:
            logger.info("Running crawl job immediately...")
            asyncio.create_task(self.run_crawl_job())

        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self._running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown(wait=True)
        self._running = False
        logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    def get_next_run_time(self) -> Optional[datetime]:
        """
        Get the next scheduled run time.

        Returns:
            Next run time as datetime or None if no job is scheduled
        """
        job = self.scheduler.get_job("crawl_job")
        if job:
            return job.next_run_time
        return None

    def run_now(self) -> None:
        """Trigger the crawl job to run immediately (in addition to schedule)."""
        logger.info("Manually triggering crawl job...")
        asyncio.create_task(self.run_crawl_job())


# Example usage
if __name__ == "__main__":
    async def on_crawl_success(results):
        """Handle successful crawl."""
        total = sum(len(articles) for articles in results.values())
        print(f"✓ Crawl successful: {total} articles")
        for category, articles in results.items():
            print(f"  - {category}: {len(articles)} articles")

    async def on_crawl_error(error):
        """Handle crawl error."""
        print(f"✗ Crawl failed: {error}")

    async def main():
        """Test scheduler."""
        # Create scheduler with callbacks
        scheduler = CrawlScheduler(
            on_success=on_crawl_success,
            on_error=on_crawl_error,
        )

        # Schedule for testing (every minute for demo)
        # In production, use: "0 9,15,21 * * *"
        scheduler.schedule("* * * * *")  # Every minute

        # Show next run time
        next_run = scheduler.get_next_run_time()
        print(f"Next scheduled run: {next_run}")

        # Start scheduler and run immediately
        scheduler.start(run_immediately=True)

        # Keep running for a while
        try:
            print("Scheduler running. Press Ctrl+C to stop.")
            await asyncio.sleep(300)  # Run for 5 minutes
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
        finally:
            scheduler.stop()

    # Run test
    asyncio.run(main())
