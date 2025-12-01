"""Unit tests for Elasticsearch client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.storage.es_client import ElasticsearchClient
from elasticsearch.exceptions import ConnectionError, NotFoundError


class TestElasticsearchClient:
    """Test suite for ElasticsearchClient class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            "elasticsearch.host": "localhost",
            "elasticsearch.port": 9200,
            "elasticsearch.username": "",
            "elasticsearch.password": "",
            "elasticsearch.index_prefix": "test_data",
        }.get(key, default))
        return config

    def test_init_with_config(self, mock_config):
        """Test client initialization with config."""
        client = ElasticsearchClient(config=mock_config)

        assert client.host == "localhost"
        assert client.port == 9200
        assert client.index_prefix == "test_data"

    def test_init_with_custom_params(self):
        """Test client initialization with custom parameters."""
        client = ElasticsearchClient(
            host="custom-host",
            port=9300,
            username="user",
            password="pass",
            index_prefix="custom"
        )

        assert client.host == "custom-host"
        assert client.port == 9300
        assert client.username == "user"
        assert client.password == "pass"
        assert client.index_prefix == "custom"

    @patch('src.storage.es_client.Elasticsearch')
    def test_connect_success(self, mock_es_class, mock_config):
        """Test successful connection."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        result = client.connect()

        assert result is True
        assert client.is_connected() is True
        mock_es.ping.assert_called_once()

    @patch('src.storage.es_client.Elasticsearch')
    def test_connect_failure(self, mock_es_class, mock_config):
        """Test connection failure."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=False)
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        result = client.connect()

        assert result is False
        assert client.is_connected() is False

    @patch('src.storage.es_client.Elasticsearch')
    def test_connect_with_auth(self, mock_es_class):
        """Test connection with authentication."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(
            host="localhost",
            port=9200,
            username="testuser",
            password="testpass"
        )
        client.connect()

        # Verify auth was passed
        call_args = mock_es_class.call_args
        assert "http_auth" in call_args[1]
        assert call_args[1]["http_auth"] == ("testuser", "testpass")

    @patch('src.storage.es_client.Elasticsearch')
    def test_close(self, mock_es_class, mock_config):
        """Test closing connection."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.close = Mock()
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()
        client.close()

        mock_es.close.assert_called_once()
        assert client.is_connected() is False

    @patch('src.storage.es_client.Elasticsearch')
    def test_create_index_success(self, mock_es_class, mock_config):
        """Test successful index creation."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=False)
        mock_es.indices.create = Mock()
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()
        result = client.create_index("test_index")

        assert result is True
        mock_es.indices.create.assert_called_once()

    @patch('src.storage.es_client.Elasticsearch')
    def test_create_index_already_exists(self, mock_es_class, mock_config):
        """Test creating index that already exists."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()
        result = client.create_index("test_index")

        assert result is True
        # Should not call create if exists
        mock_es.indices.create.assert_not_called()

    @patch('src.storage.es_client.Elasticsearch')
    def test_delete_index(self, mock_es_class, mock_config):
        """Test index deletion."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es.indices.delete = Mock()
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()
        result = client.delete_index("test_index")

        assert result is True
        mock_es.indices.delete.assert_called_once()

    @patch('src.storage.es_client.Elasticsearch')
    def test_index_document(self, mock_es_class, mock_config):
        """Test indexing a single document."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.index = Mock(return_value={"_id": "123"})
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()

        doc = {"title": "Test", "content": "Test content"}
        result = client.index_document("test_index", doc, doc_id="test-1")

        assert result is True
        mock_es.index.assert_called_once_with(
            index="test_index",
            id="test-1",
            body=doc
        )

    @patch('src.storage.es_client.Elasticsearch')
    @patch('src.storage.es_client.bulk')
    def test_bulk_index(self, mock_bulk, mock_es_class, mock_config):
        """Test bulk indexing."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es_class.return_value = mock_es

        # Mock bulk helper
        mock_bulk.return_value = (2, [])  # 2 successful, 0 failed

        client = ElasticsearchClient(config=mock_config)
        client.connect()

        docs = [
            {"title": "Doc 1", "url": "http://example.com/1"},
            {"title": "Doc 2", "url": "http://example.com/2"},
        ]
        result = client.bulk_index("test_index", docs, id_field="url")

        assert result["success"] == 2
        assert result["failed"] == 0
        mock_bulk.assert_called_once()

    @patch('src.storage.es_client.Elasticsearch')
    def test_search(self, mock_es_class, mock_config):
        """Test search functionality."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.search = Mock(return_value={
            "hits": {
                "hits": [{"_id": "1", "_source": {"title": "Test"}}],
                "total": {"value": 1}
            }
        })
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()

        query = {"match": {"title": "test"}}
        result = client.search("test_index", query, size=10)

        assert result["hits"]["total"]["value"] == 1
        assert len(result["hits"]["hits"]) == 1
        mock_es.search.assert_called_once()

    @patch('src.storage.es_client.Elasticsearch')
    def test_search_not_found(self, mock_es_class, mock_config):
        """Test search on non-existent index."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.search = Mock(side_effect=NotFoundError("Index not found"))
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()

        query = {"match_all": {}}
        result = client.search("nonexistent", query)

        # Should return empty results, not raise exception
        assert result["hits"]["total"]["value"] == 0

    @patch('src.storage.es_client.Elasticsearch')
    def test_get_document(self, mock_es_class, mock_config):
        """Test getting a document by ID."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.get = Mock(return_value={
            "_id": "test-1",
            "_source": {"title": "Test Document"}
        })
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()

        doc = client.get_document("test_index", "test-1")

        assert doc is not None
        assert doc["title"] == "Test Document"
        mock_es.get.assert_called_once()

    @patch('src.storage.es_client.Elasticsearch')
    def test_context_manager(self, mock_es_class, mock_config):
        """Test using client as context manager."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.close = Mock()
        mock_es_class.return_value = mock_es

        with ElasticsearchClient(config=mock_config) as client:
            assert client.is_connected() is True

        # Should have called close
        mock_es.close.assert_called_once()

    def test_is_connected_false_initially(self, mock_config):
        """Test that client is not connected initially."""
        client = ElasticsearchClient(config=mock_config)
        assert client.is_connected() is False

    @patch('src.storage.es_client.Elasticsearch')
    def test_index_exists(self, mock_es_class, mock_config):
        """Test checking if index exists."""
        mock_es = Mock()
        mock_es.ping = Mock(return_value=True)
        mock_es.info = Mock(return_value={"version": {"number": "7.17.0"}})
        mock_es.indices.exists = Mock(return_value=True)
        mock_es_class.return_value = mock_es

        client = ElasticsearchClient(config=mock_config)
        client.connect()

        result = client.index_exists("test_index")
        assert result is True

        mock_es.indices.exists.assert_called_once_with(index="test_index")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
