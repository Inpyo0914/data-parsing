#!/usr/bin/env python3
"""
Elasticsearch 인덱스 초기화 스크립트

이 스크립트는 Elasticsearch 인덱스를 생성하고 초기 설정을 수행합니다.
"""

import sys
sys.path.insert(0, '/home/user/data-parsing')

from src.storage.indexer import NewsIndexer
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger()


def main():
    """Elasticsearch 인덱스를 설정합니다."""
    logger.info("Starting Elasticsearch setup...")

    try:
        # Config 로드
        config = Config()
        logger.info(f"Loaded configuration")

        # Indexer 초기화
        indexer = NewsIndexer(config=config)

        # 인덱스 생성
        logger.info("Creating Elasticsearch indices...")
        indexer.setup_indices()

        logger.info("✓ Elasticsearch setup completed successfully!")

        # 상태 확인
        try:
            if indexer.es_client.is_connected():
                info = indexer.es_client.client.info()
                logger.info(f"  Elasticsearch version: {info['version']['number']}")
                logger.info(f"  Cluster name: {info['cluster_name']}")

                # 인덱스 목록
                indices = indexer.es_client.client.cat.indices(format='json')
                logger.info(f"  Total indices: {len(indices)}")
                for idx in indices:
                    if 'financial' in idx['index']:
                        logger.info(f"    - {idx['index']}: {idx['docs.count']} docs")
        except Exception as e:
            logger.warning(f"Could not retrieve status: {e}")

        return 0

    except Exception as e:
        logger.error(f"✗ Elasticsearch setup failed: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
