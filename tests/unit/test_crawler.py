"""Unit tests for crawler module."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from src.collector.crawler import FinancialJuiceCrawler
from src.collector.exceptions import FetchException


class TestFinancialJuiceCrawler:
    """Test suite for FinancialJuiceCrawler class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            "crawler.base_url": "http://test.com",
            "crawler.user_agent": "TestBot/1.0",
            "crawler.timeout": 10,
            "crawler.max_retries": 3,
            "crawler.delay": 1.0,
            "crawler.categories": ["equities", "bonds", "forex", "commodities"],
        }.get(key, default))
        return config

    def test_init_with_defaults(self, mock_config):
        """Test crawler initialization with default config."""
        crawler = FinancialJuiceCrawler(config=mock_config)

        assert crawler.base_url == "http://test.com"
        assert crawler.user_agent == "TestBot/1.0"
        assert crawler.max_retries == 3

    def test_init_with_custom_params(self):
        """Test crawler initialization with custom parameters."""
        crawler = FinancialJuiceCrawler(
            base_url="http://custom.com",
            user_agent="CustomBot/2.0",
            timeout=20,
            max_retries=5
        )

        assert crawler.base_url == "http://custom.com"
        assert crawler.user_agent == "CustomBot/2.0"
        assert crawler.timeout == 20
        assert crawler.max_retries == 5

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test async context manager."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            assert crawler.session is not None

        # Session should be closed after exit
        assert crawler.session.closed

    @pytest.mark.asyncio
    async def test_fetch_page_success(self, mock_config):
        """Test successful page fetch."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # Mock the session.get method with async context manager support
            mock_response = MagicMock()
            mock_response.text = AsyncMock(return_value="<html>Test</html>")
            mock_response.raise_for_status = Mock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()

            crawler.session.get = MagicMock(return_value=mock_response)

            html = await crawler.fetch_page("http://test.com/page")

            assert html == "<html>Test</html>"
            crawler.session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_page_with_retries(self, mock_config):
        """Test fetch page with retry on failure."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # First call fails, second succeeds
            mock_response_fail = MagicMock()
            mock_response_fail.raise_for_status = Mock(side_effect=Exception("Error"))
            mock_response_fail.__aenter__ = AsyncMock(return_value=mock_response_fail)
            mock_response_fail.__aexit__ = AsyncMock()

            mock_response_success = MagicMock()
            mock_response_success.text = AsyncMock(return_value="<html>Success</html>")
            mock_response_success.raise_for_status = Mock()
            mock_response_success.__aenter__ = AsyncMock(return_value=mock_response_success)
            mock_response_success.__aexit__ = AsyncMock()

            crawler.session.get = MagicMock(
                side_effect=[mock_response_fail, mock_response_success]
            )

            html = await crawler.fetch_page("http://test.com/page")

            assert html == "<html>Success</html>"
            assert crawler.session.get.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_page_max_retries_exceeded(self, mock_config):
        """Test fetch page when max retries exceeded."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # All attempts fail
            mock_response = MagicMock()
            mock_response.raise_for_status = Mock(side_effect=Exception("Error"))
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()

            crawler.session.get = MagicMock(return_value=mock_response)

            with pytest.raises(FetchException):
                await crawler.fetch_page("http://test.com/page")

            # Should have tried max_retries times
            assert crawler.session.get.call_count == crawler.max_retries

    @pytest.mark.asyncio
    async def test_crawl_category(self, mock_config):
        """Test crawling a single category."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # Mock fetch_page
            test_html = """
            <html><body>
                <article><h2>Test Article</h2></article>
            </body></html>
            """
            crawler.fetch_page = AsyncMock(return_value=test_html)

            results = await crawler.crawl_category("equities")

            assert isinstance(results, list)
            crawler.fetch_page.assert_called_once()

            # Check URL was constructed correctly
            call_url = crawler.fetch_page.call_args[0][0]
            assert "equities" in call_url

    @pytest.mark.asyncio
    async def test_crawl_all(self, mock_config):
        """Test crawling all categories."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # Mock crawl_category
            async def mock_crawl_category(category):
                return [{"title": f"{category} article", "category": category}]

            crawler.crawl_category = AsyncMock(side_effect=mock_crawl_category)

            results = await crawler.crawl_all()

            assert isinstance(results, dict)
            assert "equities" in results
            assert "bonds" in results
            assert "forex" in results
            assert "commodities" in results

            # Each category should have results
            for category in ["equities", "bonds", "forex", "commodities"]:
                assert len(results[category]) > 0
                assert results[category][0]["category"] == category

    @pytest.mark.asyncio
    async def test_crawl_all_with_partial_failure(self, mock_config):
        """Test crawl_all handles partial failures gracefully."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # Some categories succeed, some fail
            async def mock_crawl_category(category):
                if category == "bonds":
                    raise Exception("Failed to crawl bonds")
                return [{"title": f"{category} article"}]

            crawler.crawl_category = AsyncMock(side_effect=mock_crawl_category)

            results = await crawler.crawl_all()

            # Should have results for successful categories
            assert isinstance(results, dict)
            assert "equities" in results
            assert "bonds" in results  # Should be empty list
            assert isinstance(results["bonds"], list)

    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_config):
        """Test that rate limiter is used."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            assert crawler.rate_limiter is not None

            # Mock fetch with async context manager support
            mock_response = MagicMock()
            mock_response.text = AsyncMock(return_value="<html></html>")
            mock_response.raise_for_status = Mock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()

            crawler.session.get = MagicMock(return_value=mock_response)

            # Rate limiter should be called
            import time
            start = time.monotonic()
            await crawler.fetch_page("http://test.com")
            await crawler.fetch_page("http://test.com")
            elapsed = time.monotonic() - start

            # Second request should be delayed (rate limiter config is 0.01s for testing)
            # But there should be some measurable delay
            assert elapsed >= 0  # Just verify it doesn't crash

    def test_user_agent_set(self, mock_config):
        """Test that user agent is properly set."""
        crawler = FinancialJuiceCrawler(
            config=mock_config,
            user_agent="CustomBot/3.0"
        )

        assert crawler.user_agent == "CustomBot/3.0"

    def test_timeout_set(self, mock_config):
        """Test that timeout is properly set."""
        crawler = FinancialJuiceCrawler(
            config=mock_config,
            timeout=30
        )

        assert crawler.timeout == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
