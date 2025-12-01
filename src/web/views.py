"""
View logic for handling Elasticsearch queries and data formatting.

This module provides view classes that interact with Elasticsearch
to retrieve and format news data for templates.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from src.storage.es_client import ElasticsearchClient
from src.storage.mappings import get_index_name
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsView:
    """
    View logic for news operations.

    Handles Elasticsearch queries, pagination, filtering, and
    data formatting for display in templates.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize news view.

        Args:
            config: Configuration object
        """
        # Get config
        from src.utils.config import get_config
        if config is None:
            config = get_config()

        self.config = config
        self.index_prefix = config.get("elasticsearch.index_prefix", "financial_data")

        # Initialize ES client
        self.es_client = ElasticsearchClient(config=config)
        if not self.es_client.connect():
            logger.warning("Failed to connect to Elasticsearch in NewsView init")
            # Don't raise error - queries will handle connection check

    def list_news(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
        sort_by: str = "crawled_at"
    ) -> Dict[str, Any]:
        """
        List news articles with pagination.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            category: Optional category filter
            sort_by: Sort field (default: crawled_at)

        Returns:
            Dictionary with news list, pagination info, and metadata
        """
        # Check ES connection
        if not self.es_client.is_connected():
            logger.warning("Elasticsearch not connected in list_news")
            return {
                "articles": [],
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
                "has_prev": False,
                "has_next": False,
                "category": category,
                "error": "Database connection unavailable",
            }

        try:
            # Calculate offset
            from_offset = (page - 1) * per_page

            # Determine index to search
            if category:
                index = get_index_name(self.index_prefix, category)
            else:
                # Search all categories using wildcard
                index = f"{self.index_prefix}_*"

            # Build query
            query = {"match_all": {}}

            # Sort order
            sort = [{sort_by: {"order": "desc"}}]

            # Execute search
            results = self.es_client.search(
                index=index,
                query=query,
                size=per_page,
                from_=from_offset,
                sort=sort
            )

            # Extract hits
            hits = results.get("hits", {}).get("hits", [])
            total = results.get("hits", {}).get("total", {}).get("value", 0)

            # Format articles
            articles = [self._format_article(hit) for hit in hits]

            # Calculate pagination
            total_pages = (total + per_page - 1) // per_page

            return {
                "articles": articles,
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages,
                "category": category,
            }

        except Exception as e:
            logger.error(f"Error listing news: {e}")
            return {
                "articles": [],
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
                "has_prev": False,
                "has_next": False,
                "category": category,
                "error": str(e),
            }

    def search_news(
        self,
        query_string: str,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search news articles with filters.

        Args:
            query_string: Search query
            page: Page number (1-indexed)
            per_page: Number of items per page
            category: Optional category filter
            date_from: Optional start date (ISO format)
            date_to: Optional end date (ISO format)

        Returns:
            Dictionary with search results and pagination info
        """
        # Check ES connection
        if not self.es_client.is_connected():
            logger.warning("Elasticsearch not connected in search_news")
            return {
                "articles": [],
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
                "has_prev": False,
                "has_next": False,
                "query": query_string,
                "category": category,
                "error": "Database connection unavailable",
            }

        try:
            # Calculate offset
            from_offset = (page - 1) * per_page

            # Determine index
            if category:
                index = get_index_name(self.index_prefix, category)
            else:
                index = f"{self.index_prefix}_*"

            # Build query
            must_clauses = []

            # Text search
            if query_string:
                must_clauses.append({
                    "multi_match": {
                        "query": query_string,
                        "fields": ["title^3", "summary^2", "content"],
                        "type": "best_fields",
                    }
                })

            # Date range filter
            if date_from or date_to:
                date_range = {}
                if date_from:
                    date_range["gte"] = date_from
                if date_to:
                    date_range["lte"] = date_to

                must_clauses.append({
                    "range": {
                        "published_date": date_range
                    }
                })

            # Build final query
            if must_clauses:
                query = {
                    "bool": {
                        "must": must_clauses
                    }
                }
            else:
                query = {"match_all": {}}

            # Sort by relevance if search query, otherwise by date
            if query_string:
                sort = [{"_score": {"order": "desc"}}, {"crawled_at": {"order": "desc"}}]
            else:
                sort = [{"crawled_at": {"order": "desc"}}]

            # Execute search
            results = self.es_client.search(
                index=index,
                query=query,
                size=per_page,
                from_=from_offset,
                sort=sort
            )

            # Extract hits
            hits = results.get("hits", {}).get("hits", [])
            total = results.get("hits", {}).get("total", {}).get("value", 0)

            # Format articles
            articles = [self._format_article(hit) for hit in hits]

            # Calculate pagination
            total_pages = (total + per_page - 1) // per_page

            return {
                "articles": articles,
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages,
                "query": query_string,
                "category": category,
            }

        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return {
                "articles": [],
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
                "has_prev": False,
                "has_next": False,
                "query": query_string,
                "category": category,
                "error": str(e),
            }

    def get_news_detail(self, news_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a single news article.

        Args:
            news_id: Document ID (typically the URL)

        Returns:
            Article dictionary or None if not found
        """
        # Check ES connection
        if not self.es_client.is_connected():
            logger.warning("Elasticsearch not connected in get_news_detail")
            return None

        try:
            # Search across all indices
            index = f"{self.index_prefix}_*"

            # Try to get by ID
            query = {
                "term": {
                    "url": news_id
                }
            }

            results = self.es_client.search(index=index, query=query, size=1)

            hits = results.get("hits", {}).get("hits", [])

            if hits:
                return self._format_article(hits[0])
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting news detail: {e}")
            return None

    def get_categories_stats(self) -> Dict[str, int]:
        """
        Get article counts by category.

        Returns:
            Dictionary mapping category names to article counts
        """
        # Check ES connection
        if not self.es_client.is_connected():
            logger.warning("Elasticsearch not connected in get_categories_stats")
            return {}

        try:
            categories = ["equities", "bonds", "forex", "commodities"]
            stats = {}

            for category in categories:
                index = get_index_name(self.index_prefix, category)

                if self.es_client.index_exists(index):
                    query = {"match_all": {}}
                    results = self.es_client.search(index, query, size=0)
                    count = results.get("hits", {}).get("total", {}).get("value", 0)
                    stats[category] = count
                else:
                    stats[category] = 0

            return stats

        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return {}

    def _format_article(self, hit: Dict) -> Dict[str, Any]:
        """
        Format Elasticsearch hit into article dictionary.

        Args:
            hit: Elasticsearch hit object

        Returns:
            Formatted article dictionary
        """
        source = hit.get("_source", {})

        return {
            "id": hit.get("_id"),
            "title": source.get("title", "Untitled"),
            "summary": source.get("summary", ""),
            "content": source.get("content", ""),
            "category": source.get("category", ""),
            "author": source.get("author", ""),
            "url": source.get("url", ""),
            "source_url": source.get("source_url", ""),
            "published_date": source.get("published_date"),
            "crawled_at": source.get("crawled_at"),
            "tags": source.get("tags", []),
        }

    def close(self):
        """Close Elasticsearch connection."""
        if self.es_client:
            self.es_client.close()
