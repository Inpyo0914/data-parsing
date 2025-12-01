#!/usr/bin/env python3
"""
Test script for Phase 4 Flask web interface.
Tests basic functionality without requiring a running server.
"""

import sys
sys.path.insert(0, '/home/user/data-parsing')

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src.web.app import create_app
        from src.web.routes import main_bp, api_bp
        from src.web.views import NewsView
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test Flask app creation."""
    print("\nTesting app creation...")
    try:
        from src.web.app import create_app

        app = create_app()
        assert app is not None
        assert app.config["APP_CONFIG"] is not None
        print(f"✓ App created successfully")
        print(f"  Debug mode: {app.config['DEBUG']}")
        print(f"  Secret key configured: {len(app.config.get('SECRET_KEY', '')) > 0}")

        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_blueprints():
    """Test that blueprints are registered."""
    print("\nTesting blueprints...")
    try:
        from src.web.app import create_app

        app = create_app()

        # Check blueprints are registered
        assert 'main' in app.blueprints
        assert 'api' in app.blueprints
        print("✓ Main blueprint registered")
        print("✓ API blueprint registered")

        return True
    except Exception as e:
        print(f"✗ Blueprint test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Test that routes are accessible."""
    print("\nTesting routes...")
    try:
        from src.web.app import create_app

        app = create_app()

        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append((rule.rule, rule.endpoint))

        # Check key routes exist
        route_paths = [r[0] for r in routes]

        expected_routes = [
            '/',
            '/category/<category>',
            '/search',
            '/news/<path:news_id>',
            '/api/news',
            '/api/search',
            '/api/stats',
        ]

        for expected in expected_routes:
            # Check if route or similar exists
            found = any(expected in path for path in route_paths)
            if found:
                print(f"✓ Route exists: {expected}")
            else:
                print(f"✗ Route missing: {expected}")
                return False

        return True
    except Exception as e:
        print(f"✗ Route test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_view_initialization():
    """Test NewsView can be initialized."""
    print("\nTesting NewsView initialization...")
    try:
        from src.web.views import NewsView

        # This will try to connect to ES, but should handle failure gracefully
        view = NewsView()
        assert view is not None
        assert view.es_client is not None
        assert view.index_prefix is not None
        print(f"✓ NewsView initialized")
        print(f"  Index prefix: {view.index_prefix}")

        # Test close method
        view.close()
        print("✓ NewsView close() works")

        return True
    except Exception as e:
        print(f"✗ NewsView initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_view_methods():
    """Test NewsView methods handle no ES connection gracefully."""
    print("\nTesting NewsView methods (no ES)...")
    try:
        from src.web.views import NewsView

        view = NewsView()

        # Test list_news (should return empty results, not crash)
        result = view.list_news(page=1, per_page=10)
        assert isinstance(result, dict)
        assert "articles" in result
        assert "total" in result
        print("✓ list_news() handles no connection")

        # Test search_news
        result = view.search_news("test query", page=1, per_page=10)
        assert isinstance(result, dict)
        assert "articles" in result
        print("✓ search_news() handles no connection")

        # Test get_news_detail
        result = view.get_news_detail("test-id")
        # Should return None when not connected
        print("✓ get_news_detail() handles no connection")

        # Test get_categories_stats
        result = view.get_categories_stats()
        assert isinstance(result, dict)
        print("✓ get_categories_stats() handles no connection")

        view.close()
        return True
    except Exception as e:
        print(f"✗ NewsView methods test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_templates_exist():
    """Test that templates exist."""
    print("\nTesting template files...")
    import os
    try:
        template_dir = "/home/user/data-parsing/src/web/templates"

        expected_templates = [
            "base.html",
            "index.html",
            "category.html",
            "search.html",
            "detail.html",
            "errors/404.html",
            "errors/500.html",
        ]

        for template in expected_templates:
            path = os.path.join(template_dir, template)
            if os.path.exists(path):
                print(f"✓ Template exists: {template}")
            else:
                print(f"✗ Template missing: {template}")
                return False

        return True
    except Exception as e:
        print(f"✗ Template test error: {e}")
        return False

def test_static_files_exist():
    """Test that static files exist."""
    print("\nTesting static files...")
    import os
    try:
        static_dir = "/home/user/data-parsing/src/web/static"

        expected_files = [
            "css/style.css",
        ]

        for file in expected_files:
            path = os.path.join(static_dir, file)
            if os.path.exists(path):
                print(f"✓ Static file exists: {file}")
            else:
                print(f"✗ Static file missing: {file}")
                return False

        return True
    except Exception as e:
        print(f"✗ Static files test error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 4 Flask Web Interface Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_app_creation,
        test_blueprints,
        test_routes,
        test_news_view_initialization,
        test_news_view_methods,
        test_templates_exist,
        test_static_files_exist,
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
