"""
Elasticsearch index mappings for financial news data.

This module defines the structure of Elasticsearch indices including
field types, analyzers, and index settings.
"""

from typing import Dict, Any


# Main index mapping for financial news
FINANCIAL_NEWS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "financial_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        },
        "max_result_window": 10000  # For deep pagination
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "financial_analyzer",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    },
                    "raw": {
                        "type": "keyword"
                    }
                }
            },
            "summary": {
                "type": "text",
                "analyzer": "financial_analyzer"
            },
            "content": {
                "type": "text",
                "analyzer": "financial_analyzer"
            },
            "category": {
                "type": "keyword"
            },
            "author": {
                "type": "keyword"
            },
            "url": {
                "type": "keyword",
                "index": True  # Make searchable
            },
            "source_url": {
                "type": "keyword"
            },
            "published_date": {
                "type": "date",
                "format": "strict_date_optional_time||epoch_millis||yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss",
                "null_value": "1970-01-01T00:00:00"
            },
            "crawled_at": {
                "type": "date",
                "format": "strict_date_optional_time||epoch_millis"
            },
            "tags": {
                "type": "keyword"
            },
            "metadata": {
                "type": "object",
                "enabled": False  # Don't index, just store
            }
        }
    }
}


def get_index_name(prefix: str, category: str = None) -> str:
    """
    Generate index name.

    Args:
        prefix: Index prefix (e.g., 'financial_data')
        category: Optional category name

    Returns:
        Full index name

    Example:
        >>> get_index_name('financial_data', 'equities')
        'financial_data_equities'
        >>> get_index_name('financial_data')
        'financial_data'
    """
    if category:
        return f"{prefix}_{category}"
    return prefix


def get_alias_name(prefix: str) -> str:
    """
    Generate alias name for all category indices.

    Args:
        prefix: Index prefix

    Returns:
        Alias name

    Example:
        >>> get_alias_name('financial_data')
        'financial_data_all'
    """
    return f"{prefix}_all"


def create_index_body(custom_settings: Dict[str, Any] = None) -> Dict:
    """
    Create index body with optional custom settings.

    Args:
        custom_settings: Custom settings to merge with defaults

    Returns:
        Complete index body dict

    Example:
        >>> body = create_index_body({'number_of_shards': 2})
        >>> body['settings']['number_of_shards']
        2
    """
    import copy
    body = copy.deepcopy(FINANCIAL_NEWS_MAPPING)

    if custom_settings:
        # Merge custom settings
        body["settings"].update(custom_settings)

    return body


# Category-specific mappings (if needed)
CATEGORY_MAPPINGS = {
    "equities": FINANCIAL_NEWS_MAPPING,
    "bonds": FINANCIAL_NEWS_MAPPING,
    "forex": FINANCIAL_NEWS_MAPPING,
    "commodities": FINANCIAL_NEWS_MAPPING,
}


# Template for creating indices
INDEX_TEMPLATE = {
    "index_patterns": ["financial_data_*"],
    "template": FINANCIAL_NEWS_MAPPING,
    "priority": 1,
    "version": 1,
}


if __name__ == "__main__":
    import json

    # Print mapping for inspection
    print("Financial News Mapping:")
    print(json.dumps(FINANCIAL_NEWS_MAPPING, indent=2))

    print("\nExample index names:")
    print(f"  Equities: {get_index_name('financial_data', 'equities')}")
    print(f"  All: {get_alias_name('financial_data')}")
