"""
Elasticsearch client for managing connections and basic operations.

This module provides a wrapper around the Elasticsearch Python client
with error handling, connection management, and convenience methods.
"""

from typing import Dict, List, Optional, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import (
    ConnectionError,
    NotFoundError,
    RequestError,
)

from .mappings import FINANCIAL_NEWS_MAPPING, get_index_name
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class ElasticsearchClient:
    """
    Elasticsearch client wrapper with convenient methods.

    Provides:
    - Connection management
    - Index operations (create, delete, check existence)
    - Document operations (index, bulk index, search)
    - Error handling and logging

    Example:
        >>> client = ElasticsearchClient()
        >>> if client.connect():
        ...     client.create_index('financial_data_equities')
        ...     client.index_document('financial_data_equities', {'title': 'News'})
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        index_prefix: Optional[str] = None,
        config: Optional[Any] = None,
    ):
        """
        Initialize Elasticsearch client.

        Args:
            host: Elasticsearch host
            port: Elasticsearch port
            username: Username for authentication (optional)
            password: Password for authentication (optional)
            index_prefix: Prefix for index names
            config: Configuration object
        """
        if config is None:
            config = get_config()

        self.host = host or config.get("elasticsearch.host", "localhost")
        self.port = port or config.get("elasticsearch.port", 9200)
        self.username = username or config.get("elasticsearch.username", "")
        self.password = password or config.get("elasticsearch.password", "")
        self.index_prefix = index_prefix or config.get("elasticsearch.index_prefix", "financial_data")

        self.client: Optional[Elasticsearch] = None
        self._connected = False

        logger.info(f"Initialized ES client: {self.host}:{self.port}")

    def connect(self) -> bool:
        """
        Connect to Elasticsearch.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Build connection parameters
            conn_params = {
                "hosts": [f"{self.host}:{self.port}"],
                "timeout": 30,
                "max_retries": 3,
                "retry_on_timeout": True,
            }

            # Add authentication if provided
            if self.username and self.password:
                conn_params["http_auth"] = (self.username, self.password)

            self.client = Elasticsearch(**conn_params)

            # Test connection
            if self.client.ping():
                self._connected = True
                info = self.client.info()
                logger.info(
                    f"Connected to Elasticsearch {info['version']['number']} "
                    f"at {self.host}:{self.port}"
                )
                return True
            else:
                logger.error("Failed to ping Elasticsearch")
                return False

        except ConnectionError as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Elasticsearch: {e}")
            self._connected = False
            return False

    def close(self) -> None:
        """Close the Elasticsearch connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Closed Elasticsearch connection")

    def is_connected(self) -> bool:
        """Check if connected to Elasticsearch."""
        return self._connected and self.client is not None

    def create_index(
        self,
        index_name: str,
        mapping: Optional[Dict] = None,
    ) -> bool:
        """
        Create an index with mapping.

        Args:
            index_name: Name of the index
            mapping: Index mapping (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Elasticsearch")
            return False

        try:
            # Check if index already exists
            if self.client.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
                return True

            # Use default mapping if not provided
            if mapping is None:
                mapping = FINANCIAL_NEWS_MAPPING

            # Create index
            self.client.indices.create(index=index_name, body=mapping)
            logger.info(f"Created index: {index_name}")
            return True

        except RequestError as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating index {index_name}: {e}")
            return False

    def delete_index(self, index_name: str) -> bool:
        """
        Delete an index.

        Args:
            index_name: Name of the index to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Elasticsearch")
            return False

        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"Deleted index: {index_name}")
                return True
            else:
                logger.warning(f"Index {index_name} does not exist")
                return False

        except Exception as e:
            logger.error(f"Failed to delete index {index_name}: {e}")
            return False

    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists.

        Args:
            index_name: Name of the index

        Returns:
            True if exists, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            return self.client.indices.exists(index=index_name)
        except Exception as e:
            logger.error(f"Error checking index existence: {e}")
            return False

    def index_document(
        self,
        index: str,
        document: Dict,
        doc_id: Optional[str] = None,
    ) -> bool:
        """
        Index a single document.

        Args:
            index: Index name
            document: Document to index
            doc_id: Optional document ID (auto-generated if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Elasticsearch")
            return False

        try:
            response = self.client.index(
                index=index,
                id=doc_id,
                body=document,
            )
            logger.debug(f"Indexed document: {response['_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            return False

    def bulk_index(
        self,
        index: str,
        documents: List[Dict],
        id_field: str = "url",
    ) -> Dict[str, int]:
        """
        Bulk index multiple documents.

        Args:
            index: Index name
            documents: List of documents to index
            id_field: Field to use as document ID (default: 'url')

        Returns:
            Dictionary with 'success' and 'failed' counts
        """
        if not self.is_connected():
            logger.error("Not connected to Elasticsearch")
            return {"success": 0, "failed": len(documents)}

        if not documents:
            logger.warning("No documents to index")
            return {"success": 0, "failed": 0}

        try:
            # Prepare bulk actions
            actions = []
            for doc in documents:
                action = {
                    "_index": index,
                    "_source": doc,
                }
                # Use specified field as document ID if available
                if id_field and id_field in doc:
                    action["_id"] = doc[id_field]

                actions.append(action)

            # Execute bulk operation
            success, failed = bulk(
                self.client,
                actions,
                raise_on_error=False,
                stats_only=True,
            )

            logger.info(
                f"Bulk indexed to {index}: {success} successful, "
                f"{len(failed) if isinstance(failed, list) else failed} failed"
            )

            return {
                "success": success,
                "failed": len(failed) if isinstance(failed, list) else failed,
            }

        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return {"success": 0, "failed": len(documents)}

    def search(
        self,
        index: str,
        query: Dict,
        size: int = 10,
        from_: int = 0,
        sort: Optional[List] = None,
    ) -> Dict:
        """
        Search documents.

        Args:
            index: Index name (can use wildcards)
            query: Elasticsearch query DSL
            size: Number of results to return
            from_: Offset for pagination
            sort: Sort criteria

        Returns:
            Search results dictionary
        """
        if not self.is_connected():
            logger.error("Not connected to Elasticsearch")
            return {"hits": {"hits": [], "total": {"value": 0}}}

        try:
            body = {"query": query}
            if sort:
                body["sort"] = sort

            response = self.client.search(
                index=index,
                body=body,
                size=size,
                from_=from_,
            )

            return response

        except NotFoundError:
            logger.warning(f"Index {index} not found")
            return {"hits": {"hits": [], "total": {"value": 0}}}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"hits": {"hits": [], "total": {"value": 0}}}

    def get_document(self, index: str, doc_id: str) -> Optional[Dict]:
        """
        Get a document by ID.

        Args:
            index: Index name
            doc_id: Document ID

        Returns:
            Document dict or None if not found
        """
        if not self.is_connected():
            return None

        try:
            response = self.client.get(index=index, id=doc_id)
            return response["_source"]
        except NotFoundError:
            logger.warning(f"Document {doc_id} not found in {index}")
            return None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# Example usage
if __name__ == "__main__":
    # Test connection
    with ElasticsearchClient() as client:
        if client.is_connected():
            print("✓ Connected to Elasticsearch")

            # Create test index
            test_index = "test_financial_data"
            if client.create_index(test_index):
                print(f"✓ Created index: {test_index}")

                # Index test document
                test_doc = {
                    "title": "Test Article",
                    "category": "equities",
                    "url": "http://example.com/test",
                }
                if client.index_document(test_index, test_doc, "test-1"):
                    print("✓ Indexed document")

                # Search
                query = {"match_all": {}}
                results = client.search(test_index, query)
                print(f"✓ Search returned {results['hits']['total']['value']} results")

                # Cleanup
                client.delete_index(test_index)
                print(f"✓ Deleted index: {test_index}")
