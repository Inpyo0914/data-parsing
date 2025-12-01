#!/usr/bin/env python3
"""
Performance benchmarks for the financial news parser.

Measures:
- Crawling speed
- Parsing speed
- Elasticsearch indexing speed
- Web app response time
"""

import asyncio
import time
import statistics
from typing import List, Dict
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
import sys
sys.path.insert(0, '/home/user/data-parsing')

from src.collector.crawler import FinancialJuiceCrawler
from src.collector.parser import FinancialJuiceParser
from src.storage.indexer import NewsIndexer
from src.web.app import create_app


class PerformanceBenchmark:
    """Performance benchmark suite."""

    def __init__(self):
        self.results = {}

    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_result(self, name: str, value: float, unit: str = "ms"):
        """Print benchmark result."""
        print(f"  {name:.<50} {value:.2f} {unit}")

    def print_stats(self, name: str, values: List[float], unit: str = "ms"):
        """Print statistics for multiple measurements."""
        if not values:
            return

        mean = statistics.mean(values)
        median = statistics.median(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0

        print(f"\n  {name}:")
        print(f"    Mean:   {mean:.2f} {unit}")
        print(f"    Median: {median:.2f} {unit}")
        print(f"    StdDev: {stdev:.2f} {unit}")
        print(f"    Min:    {min(values):.2f} {unit}")
        print(f"    Max:    {max(values):.2f} {unit}")

    async def benchmark_crawler(self, iterations: int = 10):
        """Benchmark crawler performance."""
        self.print_header("Crawler Performance")

        mock_config = Mock()
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "crawler.base_url": "http://test.com",
            "crawler.user_agent": "BenchBot/1.0",
            "crawler.timeout": 10,
            "crawler.max_retries": 3,
            "crawler.delay": 0.01,  # Fast for testing
            "crawler.categories": ["equities", "bonds", "forex", "commodities"],
        }.get(key, default))

        test_html = """
        <html><body>
            <article>
                <h2>Article 1</h2>
                <p>Content 1</p>
                <a href="/1">Link</a>
            </article>
            <article>
                <h2>Article 2</h2>
                <p>Content 2</p>
                <a href="/2">Link</a>
            </article>
        </body></html>
        """

        times = []

        for i in range(iterations):
            async with FinancialJuiceCrawler(config=mock_config) as crawler:
                crawler.fetch_page = AsyncMock(return_value=test_html)

                start = time.perf_counter()
                results = await crawler.crawl_all()
                elapsed = (time.perf_counter() - start) * 1000  # ms

                times.append(elapsed)

        self.print_stats("Crawl all categories", times)

        # Calculate throughput
        avg_time = statistics.mean(times) / 1000  # seconds
        categories_per_sec = 4 / avg_time  # 4 categories
        self.print_result("Categories/second", categories_per_sec, "cat/s")

        self.results['crawler'] = {
            'mean_ms': statistics.mean(times),
            'categories_per_second': categories_per_sec
        }

    def benchmark_parser(self, iterations: int = 100):
        """Benchmark parser performance."""
        self.print_header("Parser Performance")

        parser = FinancialJuiceParser()

        test_html = """
        <html><body>
            %s
        </body></html>
        """ % "\n".join([
            f"""<article>
                <h2>Article {i}</h2>
                <p>Summary {i}</p>
                <a href="/article/{i}">Read</a>
            </article>"""
            for i in range(50)  # 50 articles
        ])

        times = []

        for i in range(iterations):
            start = time.perf_counter()
            results = parser.parse_article_list(test_html, "equities")
            elapsed = (time.perf_counter() - start) * 1000  # ms

            times.append(elapsed)

        self.print_stats("Parse 50 articles", times)

        # Calculate throughput
        avg_time = statistics.mean(times) / 1000  # seconds
        articles_per_sec = 50 / avg_time
        self.print_result("Articles/second", articles_per_sec, "art/s")

        self.results['parser'] = {
            'mean_ms': statistics.mean(times),
            'articles_per_second': articles_per_sec
        }

    @patch('src.storage.es_client.Elasticsearch')
    @patch('src.storage.es_client.bulk')
    def benchmark_indexer(self, mock_bulk, mock_es_class, iterations: int = 10):
        """Benchmark indexer performance."""
        self.print_header("Indexer Performance")

        # Setup mocks
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es.indices.create = Mock()
        mock_es.search = Mock(return_value={"hits": {"total": {"value": 0}, "hits": []}})
        mock_es_class.return_value = mock_es

        mock_bulk.return_value = (100, [])  # 100 success, 0 failed

        mock_config = Mock()
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "elasticsearch.host": "localhost",
            "elasticsearch.port": 9200,
            "elasticsearch.index_prefix": "test_data",
            "validation.required_fields": ["title", "url", "category"],
            "validation.max_title_length": 500,
        }.get(key, default))

        # Test data - 100 documents
        test_docs = {
            "equities": [
                {
                    "title": f"Article {i}",
                    "url": f"http://example.com/{i}",
                    "category": "equities",
                    "summary": f"Summary {i}"
                }
                for i in range(100)
            ]
        }

        times = []

        for i in range(iterations):
            indexer = NewsIndexer(config=mock_config)
            indexer.setup_indices()

            start = time.perf_counter()
            stats = indexer.index_news_batch(test_docs, skip_duplicates=False)
            elapsed = (time.perf_counter() - start) * 1000  # ms

            times.append(elapsed)

        self.print_stats("Index 100 documents", times)

        # Calculate throughput
        avg_time = statistics.mean(times) / 1000  # seconds
        docs_per_sec = 100 / avg_time
        self.print_result("Documents/second", docs_per_sec, "doc/s")

        self.results['indexer'] = {
            'mean_ms': statistics.mean(times),
            'docs_per_second': docs_per_sec
        }

    def benchmark_web_app(self, iterations: int = 100):
        """Benchmark web app response times."""
        self.print_header("Web App Performance")

        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()

        # Benchmark different endpoints
        endpoints = {
            'Home page': '/',
            'Category page': '/category/equities',
            'Search page': '/search',
            'API news list': '/api/news',
            'API search': '/api/search?q=test',
            'API stats': '/api/stats',
        }

        for name, endpoint in endpoints.items():
            times = []

            for i in range(iterations):
                start = time.perf_counter()
                response = client.get(endpoint)
                elapsed = (time.perf_counter() - start) * 1000  # ms

                if response.status_code == 200:
                    times.append(elapsed)

            if times:
                self.print_stats(name, times)

        # Calculate overall throughput
        all_times = []
        for endpoint in endpoints.values():
            start = time.perf_counter()
            for i in range(10):
                client.get(endpoint)
            elapsed = time.perf_counter() - start
            all_times.append(elapsed)

        avg_time = statistics.mean(all_times) / 10  # per request
        requests_per_sec = 1 / avg_time
        self.print_result("\nAverage requests/second", requests_per_sec, "req/s")

        self.results['web_app'] = {
            'requests_per_second': requests_per_sec
        }

    def print_summary(self):
        """Print summary of all benchmarks."""
        self.print_header("Performance Summary")

        if 'crawler' in self.results:
            print(f"\nCrawler:")
            print(f"  {self.results['crawler']['categories_per_second']:.2f} categories/second")

        if 'parser' in self.results:
            print(f"\nParser:")
            print(f"  {self.results['parser']['articles_per_second']:.2f} articles/second")

        if 'indexer' in self.results:
            print(f"\nIndexer:")
            print(f"  {self.results['indexer']['docs_per_second']:.2f} documents/second")

        if 'web_app' in self.results:
            print(f"\nWeb App:")
            print(f"  {self.results['web_app']['requests_per_second']:.2f} requests/second")

        print("\n" + "=" * 60)


async def main():
    """Run all benchmarks."""
    print("\n" + "=" * 60)
    print("  Financial News Parser - Performance Benchmarks")
    print("=" * 60)

    bench = PerformanceBenchmark()

    # Run benchmarks
    await bench.benchmark_crawler(iterations=10)
    bench.benchmark_parser(iterations=100)
    bench.benchmark_indexer(iterations=10)
    bench.benchmark_web_app(iterations=50)

    # Print summary
    bench.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
