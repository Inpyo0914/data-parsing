"""Elasticsearch storage and indexing modules."""

from .es_client import ElasticsearchClient
from .indexer import NewsIndexer
from .mappings import (
    FINANCIAL_NEWS_MAPPING,
    CATEGORY_MAPPINGS,
    INDEX_TEMPLATE,
    get_index_name,
    get_alias_name,
    create_index_body,
)

__all__ = [
    "ElasticsearchClient",
    "NewsIndexer",
    "FINANCIAL_NEWS_MAPPING",
    "CATEGORY_MAPPINGS",
    "INDEX_TEMPLATE",
    "get_index_name",
    "get_alias_name",
    "create_index_body",
]
