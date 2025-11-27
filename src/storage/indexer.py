"""
News indexer for storing crawled data in Elasticsearch.

This module handles the process of taking crawled news data and
storing it in Elasticsearch with proper validation and deduplication.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from .es_client import ElasticsearchClient
from .mappings import get_index_name
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class NewsIndexer:
    """
    Indexer for financial news data.

    Handles:
    - Index creation and management
    - Document validation
    - Duplicate detection
    - Bulk indexing with error handling
    - Statistics tracking

    Example:
        >>> indexer = NewsIndexer()
        >>> indexer.setup_indices()
        >>> stats = await indexer.index_news_batch(news_data)
        >>> print(f"Indexed {stats['total_success']} articles")
    """

    def __init__(
        self,
        es_client: Optional[ElasticsearchClient] = None,
        config: Optional[Any] = None,
    ):
        """
        Initialize indexer.

        Args:
            es_client: Elasticsearch client (creates new one if None)
            config: Configuration object
        """
        self.config = config or get_config()
        self.es_client = es_client or ElasticsearchClient(config=self.config)

        self.index_prefix = self.config.get(
            "elasticsearch.index_prefix",
            "financial_data"
        )

        self.categories = self.config.get(
            "crawler.categories",
            ["equities", "bonds", "forex", "commodities"]
        )

        logger.info(f"Initialized NewsIndexer with prefix: {self.index_prefix}")

    def setup_indices(self) -> bool:
        """
        Setup all required indices.

        Creates indices for all configured categories.

        Returns:
            True if all indices created successfully, False otherwise
        """
        if not self.es_client.connect():
            logger.error("Failed to connect to Elasticsearch")
            return False

        all_success = True

        for category in self.categories:
            index_name = get_index_name(self.index_prefix, category)
            if not self.es_client.create_index(index_name):
                logger.error(f"Failed to create index: {index_name}")
                all_success = False

        if all_success:
            logger.info(f"Successfully setup all indices")
        else:
            logger.warning("Some indices failed to create")

        return all_success

    def validate_document(self, doc: Dict) -> bool:
        """
        Validate a document before indexing.

        Args:
            doc: Document to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = self.config.get(
            "validation.required_fields",
            ["title", "url", "category"]
        )

        # Check required fields
        for field in required_fields:
            if field not in doc or not doc[field]:
                logger.warning(f"Document missing required field: {field}")
                return False

        # Validate category
        if doc.get("category") not in self.categories:
            logger.warning(f"Invalid category: {doc.get('category')}")
            return False

        # Check title length
        max_title_length = self.config.get("validation.max_title_length", 500)
        if len(doc.get("title", "")) > max_title_length:
            logger.warning(f"Title too long: {len(doc['title'])} chars")
            return False

        return True

    def check_duplicate(self, index: str, url: str) -> bool:
        """
        Check if a document with the same URL already exists.

        Args:
            index: Index name
            url: Document URL

        Returns:
            True if duplicate exists, False otherwise
        """
        if not self.es_client.is_connected():
            return False

        try:
            query = {
                "term": {
                    "url.keyword": url
                }
            }

            results = self.es_client.search(index, query, size=1)
            return results["hits"]["total"]["value"] > 0

        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return False

    def index_news(
        self,
        news_list: List[Dict],
        category: str,
        skip_duplicates: bool = True,
    ) -> Dict[str, int]:
        """
        Index a list of news articles.

        Args:
            news_list: List of news dictionaries
            category: Category name
            skip_duplicates: Skip documents that already exist

        Returns:
            Dictionary with statistics
        """
        if not self.es_client.is_connected():
            if not self.es_client.connect():
                logger.error("Failed to connect to Elasticsearch")
                return {"success": 0, "failed": len(news_list), "skipped": 0}

        index_name = get_index_name(self.index_prefix, category)

        # Ensure index exists
        if not self.es_client.index_exists(index_name):
            self.es_client.create_index(index_name)

        validated_docs = []
        skipped = 0

        for doc in news_list:
            # Validate document
            if not self.validate_document(doc):
                logger.debug(f"Skipping invalid document: {doc.get('title', 'N/A')}")
                skipped += 1
                continue

            # Check for duplicates
            if skip_duplicates and self.check_duplicate(index_name, doc["url"]):
                logger.debug(f"Skipping duplicate: {doc['url']}")
                skipped += 1
                continue

            validated_docs.append(doc)

        # Bulk index
        if validated_docs:
            result = self.es_client.bulk_index(
                index_name,
                validated_docs,
                id_field="url"
            )

            logger.info(
                f"Indexed {result['success']} documents to {index_name}, "
                f"{result['failed']} failed, {skipped} skipped"
            )

            return {
                "success": result["success"],
                "failed": result["failed"],
                "skipped": skipped,
            }
        else:
            logger.info(f"No documents to index for {category}")
            return {"success": 0, "failed": 0, "skipped": skipped}

    def index_news_batch(
        self,
        news_data: Dict[str, List[Dict]],
        skip_duplicates: bool = True,
    ) -> Dict[str, Any]:
        """
        Index news from multiple categories.

        Args:
            news_data: Dictionary mapping categories to news lists
            skip_duplicates: Skip documents that already exist

        Returns:
            Dictionary with overall statistics
        """
        stats = {
            "total_success": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "by_category": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        for category, news_list in news_data.items():
            result = self.index_news(news_list, category, skip_duplicates)

            stats["by_category"][category] = result
            stats["total_success"] += result["success"]
            stats["total_failed"] += result["failed"]
            stats["total_skipped"] += result["skipped"]

        logger.info(
            f"Batch indexing complete: {stats['total_success']} success, "
            f"{stats['total_failed']} failed, {stats['total_skipped']} skipped"
        )

        return stats

    def get_index_stats(self, category: Optional[str] = None) -> Dict:
        """
        Get statistics for an index.

        Args:
            category: Category name (None for all categories)

        Returns:
            Statistics dictionary
        """
        if not self.es_client.is_connected():
            self.es_client.connect()

        if category:
            indices = [get_index_name(self.index_prefix, category)]
        else:
            indices = [
                get_index_name(self.index_prefix, cat)
                for cat in self.categories
            ]

        stats = {}

        for index in indices:
            if self.es_client.index_exists(index):
                # Get document count
                query = {"match_all": {}}
                result = self.es_client.search(index, query, size=0)
                count = result["hits"]["total"]["value"]
                stats[index] = {"document_count": count}
            else:
                stats[index] = {"document_count": 0, "exists": False}

        return stats

    def clear_index(self, category: str) -> bool:
        """
        Clear all documents from a category index.

        Args:
            category: Category name

        Returns:
            True if successful, False otherwise
        """
        index_name = get_index_name(self.index_prefix, category)

        if not self.es_client.is_connected():
            self.es_client.connect()

        return self.es_client.delete_index(index_name)


# Example usage
if __name__ == "__main__":
    # Test indexer
    indexer = NewsIndexer()

    # Setup indices
    if indexer.setup_indices():
        print("✓ Indices setup complete")

        # Test data
        test_news = {
            "equities": [
                {
                    "title": "Stock Market Update",
                    "summary": "Markets rally on positive news",
                    "url": "http://example.com/stock-1",
                    "category": "equities",
                    "crawled_at": datetime.utcnow().isoformat(),
                }
            ]
        }

        # Index test data
        stats = indexer.index_news_batch(test_news)
        print(f"✓ Indexed: {stats['total_success']} documents")

        # Get stats
        index_stats = indexer.get_index_stats()
        print(f"✓ Index stats: {index_stats}")
