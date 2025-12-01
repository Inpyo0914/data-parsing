"""Integration tests for crawl-parse-store pipeline."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.collector.crawler import FinancialJuiceCrawler
from src.collector.parser import FinancialJuiceParser
from src.storage.indexer import NewsIndexer
from src.storage.es_client import ElasticsearchClient


class TestCrawlParseStorePipeline:
    """Test suite for complete data pipeline."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            "crawler.base_url": "http://test.com",
            "crawler.user_agent": "TestBot/1.0",
            "crawler.timeout": 10,
            "crawler.max_retries": 3,
            "crawler.delay": 0.1,  # Fast for testing
            "crawler.categories": ["equities", "bonds"],
            "elasticsearch.host": "localhost",
            "elasticsearch.port": 9200,
            "elasticsearch.index_prefix": "test_data",
            "validation.required_fields": ["title", "url", "category"],
            "validation.max_title_length": 500,
        }.get(key, default))
        return config

    @pytest.mark.asyncio
    async def test_crawl_and_parse(self, mock_config):
        """Test crawling and parsing workflow."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # Mock HTTP response
            test_html = """
            <html><body>
                <article>
                    <h2>Stock Market Rises</h2>
                    <p class="summary">Markets up 2%</p>
                    <a href="/article/1">Read more</a>
                </article>
                <article>
                    <h2>Bond Yields Fall</h2>
                    <p class="summary">Treasury yields drop</p>
                    <a href="/article/2">Read more</a>
                </article>
            </body></html>
            """
            crawler.fetch_page = AsyncMock(return_value=test_html)

            # Crawl all categories
            results = await crawler.crawl_all()

            # Verify results structure
            assert isinstance(results, dict)
            assert "equities" in results
            assert "bonds" in results

            # Verify all categories were processed
            for category in ["equities", "bonds"]:
                assert isinstance(results[category], list)

    @pytest.mark.asyncio
    @patch('src.storage.es_client.Elasticsearch')
    async def test_parse_and_store(self, mock_es_class, mock_config):
        """Test parsing and storing workflow."""
        # Setup mock ES
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es.indices.create = Mock()
        mock_es.search = Mock(return_value={"hits": {"total": {"value": 0}, "hits": []}})
        mock_es_class.return_value = mock_es

        # Mock bulk helper
        with patch('src.storage.es_client.bulk') as mock_bulk:
            mock_bulk.return_value = (2, [])  # 2 success, 0 failed

            # Create indexer
            indexer = NewsIndexer(config=mock_config)
            indexer.setup_indices()

            # Test data
            news_data = {
                "equities": [
                    {
                        "title": "Stock Market Update",
                        "summary": "Markets rally",
                        "url": "http://example.com/stock-1",
                        "category": "equities",
                    },
                    {
                        "title": "Tech Stocks Soar",
                        "summary": "Tech sector gains",
                        "url": "http://example.com/stock-2",
                        "category": "equities",
                    }
                ]
            }

            # Index news
            stats = indexer.index_news_batch(news_data, skip_duplicates=False)

            # Verify stats
            assert stats["total_success"] >= 0
            assert "equities" in stats["by_category"]

    @pytest.mark.asyncio
    @patch('src.storage.es_client.Elasticsearch')
    async def test_full_pipeline(self, mock_es_class, mock_config):
        """Test complete pipeline from crawl to store."""
        # Setup mock ES
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es.indices.create = Mock()
        mock_es.search = Mock(return_value={"hits": {"total": {"value": 0}, "hits": []}})
        mock_es_class.return_value = mock_es

        with patch('src.storage.es_client.bulk') as mock_bulk:
            mock_bulk.return_value = (10, [])

            # Step 1: Crawl
            async with FinancialJuiceCrawler(config=mock_config) as crawler:
                test_html = """
                <html><body>
                    <article>
                        <h2>Market News</h2>
                        <a href="http://example.com/news">Link</a>
                    </article>
                </body></html>
                """
                crawler.fetch_page = AsyncMock(return_value=test_html)
                crawled_data = await crawler.crawl_all()

            # Step 2: Store
            indexer = NewsIndexer(config=mock_config)
            indexer.setup_indices()

            # Index the crawled data
            stats = indexer.index_news_batch(crawled_data, skip_duplicates=False)

            # Verify pipeline completed
            assert isinstance(crawled_data, dict)
            assert isinstance(stats, dict)
            assert "total_success" in stats

    @pytest.mark.asyncio
    async def test_pipeline_with_invalid_data(self, mock_config):
        """Test pipeline handles invalid data gracefully."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            # Malformed HTML
            bad_html = "<article><h2>No closing tags"
            crawler.fetch_page = AsyncMock(return_value=bad_html)

            # Should not crash
            results = await crawler.crawl_all()
            assert isinstance(results, dict)

    @pytest.mark.asyncio
    @patch('src.storage.es_client.Elasticsearch')
    async def test_validation_filters_invalid_docs(self, mock_es_class, mock_config):
        """Test that validation filters out invalid documents."""
        # Setup mock ES
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es_class.return_value = mock_es

        with patch('src.storage.es_client.bulk') as mock_bulk:
            mock_bulk.return_value = (1, [])  # Only 1 valid document

            indexer = NewsIndexer(config=mock_config)
            indexer.setup_indices()

            # Mix of valid and invalid documents
            news_data = {
                "equities": [
                    {
                        # Valid document
                        "title": "Valid Article",
                        "url": "http://example.com/valid",
                        "category": "equities",
                    },
                    {
                        # Invalid: missing title
                        "url": "http://example.com/no-title",
                        "category": "equities",
                    },
                    {
                        # Invalid: missing URL
                        "title": "No URL Article",
                        "category": "equities",
                    },
                    {
                        # Invalid: wrong category
                        "title": "Wrong Category",
                        "url": "http://example.com/wrong",
                        "category": "invalid_category",
                    }
                ]
            }

            stats = indexer.index_news_batch(news_data, skip_duplicates=False)

            # Only 1 should be indexed, 3 skipped
            assert stats["total_skipped"] == 3

    @pytest.mark.asyncio
    async def test_concurrent_crawling(self, mock_config):
        """Test that concurrent crawling works correctly."""
        async with FinancialJuiceCrawler(config=mock_config) as crawler:
            call_count = 0

            async def mock_fetch(url):
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.01)  # Simulate network delay
                return f"<html><body><h1>Page {call_count}</h1></body></html>"

            crawler.fetch_page = AsyncMock(side_effect=mock_fetch)

            # Crawl multiple categories concurrently
            results = await crawler.crawl_all()

            # Should have called fetch for each category
            assert call_count >= 2  # At least equities and bonds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
