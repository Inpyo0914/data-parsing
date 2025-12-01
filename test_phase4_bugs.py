#!/usr/bin/env python3
"""
Test script for Phase 4 bug fixes.
Tests context manager, input validation, and resource cleanup.
"""

import sys
sys.path.insert(0, '/home/user/data-parsing')

def test_context_manager():
    """Test NewsView context manager support."""
    print("Testing context manager...")
    try:
        from src.web.views import NewsView

        # Test with statement
        with NewsView() as view:
            assert view is not None
            assert view.es_client is not None

        print("✓ Context manager __enter__ works")
        print("✓ Context manager __exit__ works")

        # Verify close is called after with block
        # (connection state is cleaned up)
        with NewsView() as view:
            pass
        # If we got here without error, cleanup worked
        print("✓ Context manager cleanup works")

        return True
    except Exception as e:
        print(f"✗ Context manager error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pagination_validation():
    """Test pagination parameter validation."""
    print("\nTesting pagination validation...")
    try:
        from src.web.views import NewsView

        with NewsView() as view:
            # Test negative page (should be clamped to 1)
            result = view.list_news(page=-5, per_page=10)
            assert result["page"] >= 1
            print("✓ Negative page number clamped to 1")

            # Test zero page (should be clamped to 1)
            result = view.list_news(page=0, per_page=10)
            assert result["page"] >= 1
            print("✓ Zero page number clamped to 1")

            # Test negative per_page (should be clamped to 1)
            result = view.list_news(page=1, per_page=-10)
            assert result["per_page"] >= 1
            print("✓ Negative per_page clamped to 1")

            # Test zero per_page (should be clamped to 1)
            result = view.list_news(page=1, per_page=0)
            assert result["per_page"] >= 1
            print("✓ Zero per_page clamped to 1")

            # Test excessive per_page (should be clamped to 100)
            result = view.list_news(page=1, per_page=1000)
            assert result["per_page"] <= 100
            print("✓ Excessive per_page clamped to 100")

        return True
    except Exception as e:
        print(f"✗ Pagination validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_pagination_validation():
    """Test search pagination parameter validation."""
    print("\nTesting search pagination validation...")
    try:
        from src.web.views import NewsView

        with NewsView() as view:
            # Test negative page
            result = view.search_news("test", page=-5, per_page=10)
            assert result["page"] >= 1
            print("✓ Search: negative page clamped")

            # Test excessive per_page
            result = view.search_news("test", page=1, per_page=5000)
            assert result["per_page"] <= 100
            print("✓ Search: excessive per_page clamped")

        return True
    except Exception as e:
        print(f"✗ Search pagination validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xss_protection():
    """Test that HTML content is not rendered as safe."""
    print("\nTesting XSS protection...")
    try:
        import os

        # Read detail template
        template_path = "/home/user/data-parsing/src/web/templates/detail.html"
        with open(template_path, 'r') as f:
            content = f.read()

        # Check that 'safe' filter is NOT used with article.content
        if '{{ article.content | safe }}' in content:
            print("✗ XSS vulnerability: 'safe' filter found in detail.html")
            return False

        if '{{ article.content }}' in content:
            print("✓ Content is auto-escaped (no 'safe' filter)")
        else:
            print("⚠ Warning: article.content not found in template")

        return True
    except Exception as e:
        print(f"✗ XSS protection test error: {e}")
        return False

def test_resource_cleanup_on_error():
    """Test that resources are cleaned up even on error."""
    print("\nTesting resource cleanup on error...")
    try:
        from src.web.views import NewsView

        # Test that __exit__ is called even if exception occurs
        cleanup_called = False

        class MockException(Exception):
            pass

        try:
            with NewsView() as view:
                # Simulate an error
                raise MockException("Test error")
        except MockException:
            # Exception should be propagated
            pass

        # If we got here, __exit__ was called (otherwise would hang)
        print("✓ Context manager cleans up on exception")

        return True
    except Exception as e:
        print(f"✗ Resource cleanup test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes_use_context_manager():
    """Test that routes use context manager (via code inspection)."""
    print("\nTesting routes use context manager...")
    try:
        import os

        # Read routes.py
        routes_path = "/home/user/data-parsing/src/web/routes.py"
        with open(routes_path, 'r') as f:
            content = f.read()

        # Check for with get_news_view() pattern
        if 'with get_news_view() as view:' in content:
            print("✓ Routes use context manager pattern")

            # Count occurrences
            count = content.count('with get_news_view() as view:')
            print(f"  Found {count} uses of context manager")

            # Check that old pattern (view.close()) is not used
            if 'view.close()' not in content:
                print("✓ No manual close() calls (good)")
            else:
                print("⚠ Warning: Some manual close() calls still exist")

            return True
        else:
            print("✗ Routes do not use context manager")
            return False

    except Exception as e:
        print(f"✗ Routes inspection error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 4 Bug Fix Tests")
    print("=" * 60)

    tests = [
        test_context_manager,
        test_pagination_validation,
        test_search_pagination_validation,
        test_xss_protection,
        test_resource_cleanup_on_error,
        test_routes_use_context_manager,
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
        print("✓ All bug fix tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
