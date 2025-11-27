"""
Web crawler for FinancialJuice website.

This module provides asynchronous web crawling functionality with
rate limiting, retry logic, and error handling.
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

from .rate_limiter import RateLimiter
from .parser import FinancialJuiceParser
from .exceptions import FetchException, CrawlerException
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class FinancialJuiceCrawler:
    """
    Asynchronous web crawler for FinancialJuice website.

    Features:
    - Async HTTP requests with aiohttp
    - Rate limiting to avoid server overload
    - Automatic retry with exponential backoff
    - HTML parsing and data extraction
    - Proper resource cleanup

    Example:
        >>> config = get_config()
        >>> async with FinancialJuiceCrawler(config) as crawler:
        ...     news = await crawler.crawl_category('equities')
        ...     print(f"Found {len(news)} articles")
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        base_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
    ):
        """
        Initialize crawler.

        Args:
            config: Configuration object (uses get_config() if None)
            base_url: Base URL for FinancialJuice
            user_agent: User agent string
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            delay: Delay between requests in seconds
        """
        # Load config
        if config is None:
            config = get_config()

        # Set crawler parameters
        self.base_url = base_url or config.get("crawler.base_url", "https://www.financialjuice.com")
        self.user_agent = user_agent or config.get("crawler.user_agent", "Mozilla/5.0")
        self.timeout = timeout or config.get("crawler.timeout", 30)
        self.max_retries = max_retries or config.get("crawler.max_retries", 3)
        delay_value = delay if delay is not None else config.get("crawler.delay", 2)

        # Initialize components
        self.rate_limiter = RateLimiter(delay=float(delay_value))
        self.parser = FinancialJuiceParser(base_url=self.base_url)
        self.session: Optional[aiohttp.ClientSession] = None

        # Get categories from config
        self.categories = config.get("crawler.categories", [
            "equities", "bonds", "forex", "commodities"
        ])

        logger.info(
            f"Initialized crawler: base_url={self.base_url}, "
            f"timeout={self.timeout}s, max_retries={self.max_retries}, "
            f"delay={delay_value}s"
        )

    async def __aenter__(self):
        """Async context manager entry - create session."""
        headers = {"User-Agent": self.user_agent}
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
        )
        logger.debug("Created aiohttp session")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close session."""
        if self.session:
            await self.session.close()
            logger.debug("Closed aiohttp session")
        return False

    async def fetch_page(self, url: str) -> str:
        """
        Fetch a single page with rate limiting and retries.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string

        Raises:
            FetchException: If fetching fails after all retries
        """
        if not self.session:
            raise CrawlerException("Session not initialized. Use async with context manager.")

        # Ensure absolute URL
        if not url.startswith("http"):
            url = urljoin(self.base_url, url)

        for attempt in range(self.max_retries):
            try:
                async with self.rate_limiter:
                    logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")

                    async with self.session.get(url) as response:
                        response.raise_for_status()
                        html = await response.text()
                        logger.info(f"Successfully fetched {url} ({len(html)} bytes)")
                        return html

            except aiohttp.ClientError as e:
                logger.warning(f"Fetch failed (attempt {attempt + 1}): {e}")

                if attempt == self.max_retries - 1:
                    raise FetchException(f"Failed to fetch {url} after {self.max_retries} attempts: {e}")

                # Exponential backoff
                wait_time = 2 ** attempt
                logger.debug(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                raise FetchException(f"Unexpected error: {e}")

        raise FetchException(f"Failed to fetch {url}")

    async def crawl_category(self, category: str) -> List[Dict]:
        """
        Crawl a specific category.

        Args:
            category: Category name (equities, bonds, forex, commodities)

        Returns:
            List of article dictionaries

        Raises:
            CrawlerException: If crawling fails
        """
        try:
            # Construct category URL (adjust based on actual site structure)
            category_url = f"{self.base_url}/{category}"

            logger.info(f"Crawling category: {category}")

            # Fetch page
            html = await self.fetch_page(category_url)

            # Parse articles
            articles = self.parser.parse_article_list(html, category)

            logger.info(f"Found {len(articles)} articles in {category}")

            return articles

        except Exception as e:
            logger.error(f"Failed to crawl category {category}: {e}")
            raise CrawlerException(f"Crawl failed for {category}: {e}")

    async def crawl_all(self) -> Dict[str, List[Dict]]:
        """
        Crawl all configured categories.

        Returns:
            Dictionary mapping category names to article lists

        Example:
            >>> result = await crawler.crawl_all()
            >>> print(result.keys())  # ['equities', 'bonds', 'forex', 'commodities']
        """
        logger.info(f"Starting crawl for {len(self.categories)} categories")

        # Create tasks for all categories
        tasks = [
            self.crawl_category(category)
            for category in self.categories
        ]

        # Execute concurrently and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Organize results by category
        crawl_results = {}
        for category, result in zip(self.categories, results):
            if isinstance(result, Exception):
                logger.error(f"Category {category} failed: {result}")
                crawl_results[category] = []
            else:
                crawl_results[category] = result

        total_articles = sum(len(articles) for articles in crawl_results.values())
        logger.info(f"Crawl complete: {total_articles} total articles across {len(self.categories)} categories")

        return crawl_results

    async def crawl_article_detail(self, url: str) -> Dict:
        """
        Fetch and parse a detailed article page.

        Args:
            url: Article URL

        Returns:
            Dictionary with detailed article information
        """
        try:
            html = await self.fetch_page(url)
            return self.parser.parse_article_detail(html)

        except Exception as e:
            logger.error(f"Failed to crawl article detail {url}: {e}")
            raise CrawlerException(f"Failed to fetch article detail: {e}")

    def update_parser_selectors(self, **selectors):
        """
        Update parser CSS selectors.

        This is useful when you need to adjust selectors based on
        the actual website structure.

        Args:
            **selectors: Keyword arguments for selector updates

        Example:
            >>> crawler.update_parser_selectors(
            ...     article_list=".news-article",
            ...     title="h1.headline"
            ... )
        """
        self.parser.update_selectors(**selectors)
        logger.info("Updated parser selectors")


# Example usage
if __name__ == "__main__":
    async def main():
        """Test crawler functionality."""
        from src.utils.config import get_config

        config = get_config()

        async with FinancialJuiceCrawler(config) as crawler:
            # Test single category
            try:
                articles = await crawler.crawl_category("equities")
                print(f"\nFound {len(articles)} articles in equities:")
                for article in articles[:3]:  # Show first 3
                    print(f"  - {article.get('title', 'N/A')}")
            except Exception as e:
                print(f"Error: {e}")

            # Test all categories
            # results = await crawler.crawl_all()
            # for category, articles in results.items():
            #     print(f"{category}: {len(articles)} articles")

    # Run test
    asyncio.run(main())
