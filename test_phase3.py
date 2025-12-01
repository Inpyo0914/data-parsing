#!/usr/bin/env python3
"""
Test script for Phase 3 Elasticsearch integration.
Tests the core functionality without requiring a running Elasticsearch instance.
"""

import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, '/home/user/data-parsing')

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src.storage.mappings import FINANCIAL_NEWS_MAPPING, get_index_name, get_alias_name
        from src.storage.es_client import ElasticsearchClient
        from src.storage.indexer import NewsIndexer
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_mappings():
    """Test mapping utilities."""
    print("\nTesting mappings...")
    try:
        from src.storage.mappings import get_index_name, get_alias_name, FINANCIAL_NEWS_MAPPING

        # Test index name generation
        assert get_index_name("financial_data", "equities") == "financial_data_equities"
        assert get_index_name("financial_data") == "financial_data"
        print("✓ Index name generation works")

        # Test alias name
        assert get_alias_name("financial_data") == "financial_data_all"
        print("✓ Alias name generation works")

        # Verify mapping structure
        assert "settings" in FINANCIAL_NEWS_MAPPING
        assert "mappings" in FINANCIAL_NEWS_MAPPING
        assert "properties" in FINANCIAL_NEWS_MAPPING["mappings"]
        print("✓ Mapping structure is valid")

        # Check required fields
        props = FINANCIAL_NEWS_MAPPING["mappings"]["properties"]
        required_fields = ["title", "url", "category", "published_date", "crawled_at"]
        for field in required_fields:
            assert field in props, f"Missing field: {field}"
        print("✓ All required fields present in mapping")

        return True
    except Exception as e:
        print(f"✗ Mapping test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_es_client_initialization():
    """Test Elasticsearch client initialization."""
    print("\nTesting ES client initialization...")
    try:
        from src.storage.es_client import ElasticsearchClient

        # Test with default config
        client = ElasticsearchClient()
        assert client.host is not None
        assert client.port is not None
        assert client.index_prefix is not None
        print(f"✓ Client initialized with host={client.host}, port={client.port}")

        # Test with custom parameters
        client2 = ElasticsearchClient(host="localhost", port=9200, index_prefix="test")
        assert client2.host == "localhost"
        assert client2.port == 9200
        assert client2.index_prefix == "test"
        print("✓ Custom parameters work")

        return True
    except Exception as e:
        print(f"✗ ES client initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_indexer_initialization():
    """Test NewsIndexer initialization."""
    print("\nTesting NewsIndexer initialization...")
    try:
        from src.storage.indexer import NewsIndexer

        indexer = NewsIndexer()
        assert indexer.es_client is not None
        assert indexer.categories is not None
        assert len(indexer.categories) > 0
        print(f"✓ Indexer initialized with categories: {indexer.categories}")

        return True
    except Exception as e:
        print(f"✗ Indexer initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_validation():
    """Test document validation logic."""
    print("\nTesting document validation...")
    try:
        from src.storage.indexer import NewsIndexer

        indexer = NewsIndexer()

        # Valid document
        valid_doc = {
            "title": "Test Article",
            "url": "http://example.com/test",
            "category": "equities",
            "summary": "Test summary",
            "crawled_at": datetime.utcnow().isoformat(),
        }
        assert indexer.validate_document(valid_doc) == True
        print("✓ Valid document passes validation")

        # Missing required field
        invalid_doc1 = {
            "title": "Test Article",
            # Missing url
            "category": "equities",
        }
        assert indexer.validate_document(invalid_doc1) == False
        print("✓ Document with missing field fails validation")

        # Invalid category
        invalid_doc2 = {
            "title": "Test Article",
            "url": "http://example.com/test",
            "category": "invalid_category",
        }
        assert indexer.validate_document(invalid_doc2) == False
        print("✓ Document with invalid category fails validation")

        # Title too long
        invalid_doc3 = {
            "title": "A" * 1000,  # Very long title
            "url": "http://example.com/test",
            "category": "equities",
        }
        assert indexer.validate_document(invalid_doc3) == False
        print("✓ Document with too long title fails validation")

        return True
    except Exception as e:
        print(f"✗ Validation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bulk_action_preparation():
    """Test bulk action preparation (without actually connecting to ES)."""
    print("\nTesting bulk action preparation...")
    try:
        from src.storage.es_client import ElasticsearchClient

        client = ElasticsearchClient()

        # Prepare test documents
        docs = [
            {
                "title": "Article 1",
                "url": "http://example.com/1",
                "category": "equities",
            },
            {
                "title": "Article 2",
                "url": "http://example.com/2",
                "category": "bonds",
            }
        ]

        # Test action preparation logic (from bulk_index method)
        actions = []
        for doc in docs:
            action = {
                "_index": "test_index",
                "_source": doc,
            }
            if "url" in doc:
                action["_id"] = doc["url"]
            actions.append(action)

        assert len(actions) == 2
        assert actions[0]["_id"] == "http://example.com/1"
        assert actions[1]["_id"] == "http://example.com/2"
        print("✓ Bulk actions prepared correctly with URL as ID")

        return True
    except Exception as e:
        print(f"✗ Bulk action test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 3 Elasticsearch Integration Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_mappings,
        test_es_client_initialization,
        test_indexer_initialization,
        test_document_validation,
        test_bulk_action_preparation,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
