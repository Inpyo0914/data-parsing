#!/usr/bin/env python3
"""
데이터 수집 실행 스크립트

이 스크립트는 FinancialJuice에서 데이터를 수집하고 Elasticsearch에 저장합니다.
"""

import sys
sys.path.insert(0, '/home/user/data-parsing')

import asyncio
from datetime import datetime
from src.collector.crawler import FinancialJuiceCrawler
from src.storage.indexer import NewsIndexer
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger()


async def main():
    """데이터 수집 및 저장을 실행합니다."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting data collection")
    logger.info(f"Start time: {start_time.isoformat()}")
    logger.info("=" * 60)

    try:
        # Config 로드
        config = Config()

        # Step 1: 크롤링
        logger.info("Step 1: Crawling data from FinancialJuice...")
        async with FinancialJuiceCrawler(config=config) as crawler:
            news_data = await crawler.crawl_all()

        # 수집된 데이터 통계
        total_articles = sum(len(articles) for articles in news_data.values())
        logger.info(f"✓ Crawled {total_articles} articles")

        for category, articles in news_data.items():
            logger.info(f"  - {category}: {len(articles)} articles")

        if total_articles == 0:
            logger.warning("No articles collected. Exiting.")
            return 0

        # Step 2: Elasticsearch에 저장
        logger.info("Step 2: Indexing to Elasticsearch...")
        indexer = NewsIndexer(config=config)
        indexer.setup_indices()

        stats = indexer.index_news_batch(news_data, skip_duplicates=True)

        # 저장 결과
        logger.info(f"✓ Indexing completed")
        logger.info(f"  - Total success: {stats['total_success']}")
        logger.info(f"  - Total skipped: {stats['total_skipped']}")
        logger.info(f"  - Total failed: {stats['total_failed']}")

        for category, cat_stats in stats['by_category'].items():
            logger.info(f"  - {category}: "
                       f"{cat_stats['success']} success, "
                       f"{cat_stats['skipped']} skipped, "
                       f"{cat_stats['failed']} failed")

        # 완료
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("Data collection completed successfully!")
        logger.info(f"End time: {end_time.isoformat()}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"✗ Data collection failed: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
