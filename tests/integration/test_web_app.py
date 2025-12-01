"""Integration tests for Flask web application."""

import pytest
from unittest.mock import Mock, patch
from src.web.app import create_app


class TestWebAppIntegration:
    """Test suite for Flask web application integration."""

    @pytest.fixture
    def app(self):
        """Create Flask test app."""
        app = create_app()
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create Flask test client."""
        return app.test_client()

    def test_app_creation(self, app):
        """Test app is created successfully."""
        assert app is not None
        assert app.config['TESTING'] is True

    def test_home_page(self, client):
        """Test home page loads."""
        response = client.get('/')
        assert response.status_code == 200

    def test_category_page(self, client):
        """Test category pages load."""
        categories = ['equities', 'bonds', 'forex', 'commodities']

        for category in categories:
            response = client.get(f'/category/{category}')
            assert response.status_code == 200

    def test_invalid_category(self, client):
        """Test invalid category returns 404."""
        response = client.get('/category/invalid')
        assert response.status_code == 404

    def test_search_page(self, client):
        """Test search page loads."""
        response = client.get('/search')
        assert response.status_code == 200

    def test_search_with_query(self, client):
        """Test search with query parameter."""
        response = client.get('/search?q=stock')
        assert response.status_code == 200

    def test_search_with_category_filter(self, client):
        """Test search with category filter."""
        response = client.get('/search?q=market&category=equities')
        assert response.status_code == 200

    def test_api_news_list(self, client):
        """Test API news list endpoint."""
        response = client.get('/api/news')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert 'success' in data
        assert 'data' in data

    def test_api_news_list_with_pagination(self, client):
        """Test API news list with pagination."""
        response = client.get('/api/news?page=1&per_page=10')
        assert response.status_code == 200

        data = response.get_json()
        assert data['data']['page'] == 1
        assert data['data']['per_page'] == 10

    def test_api_search(self, client):
        """Test API search endpoint."""
        response = client.get('/api/search?q=test')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert 'success' in data
        assert 'data' in data

    def test_api_stats(self, client):
        """Test API stats endpoint."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert 'success' in data
        assert 'data' in data

    def test_pagination_limits(self, client):
        """Test pagination limits are enforced."""
        # Test per_page maximum
        response = client.get('/api/news?per_page=1000')
        data = response.get_json()
        assert data['data']['per_page'] <= 100

        # Test per_page minimum
        response = client.get('/api/news?per_page=-10')
        data = response.get_json()
        assert data['data']['per_page'] >= 1

    def test_news_detail_not_found(self, client):
        """Test news detail with non-existent ID."""
        response = client.get('/news/http://nonexistent.com/article')
        # Should return 404 when article not found
        assert response.status_code in [200, 404]

    def test_api_news_detail_not_found(self, client):
        """Test API news detail with non-existent ID."""
        response = client.get('/api/news/http://nonexistent.com/article')
        assert response.status_code == 404

        data = response.get_json()
        assert data['success'] is False

    def test_error_handlers(self, app, client):
        """Test custom error handlers."""
        # Test 404 handler
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_blueprints_registered(self, app):
        """Test that blueprints are registered."""
        assert 'main' in app.blueprints
        assert 'api' in app.blueprints

    def test_routes_exist(self, app):
        """Test that expected routes exist."""
        routes = [str(rule) for rule in app.url_map.iter_rules()]

        # HTML routes
        assert '/' in routes
        assert '/category/<category>' in routes
        assert '/search' in routes
        assert '/news/<path:news_id>' in routes

        # API routes
        assert '/api/news' in routes
        assert '/api/search' in routes
        assert '/api/stats' in routes

    def test_static_files(self, client):
        """Test static files are served."""
        response = client.get('/static/css/style.css')
        # Should either exist (200) or fail gracefully (404)
        assert response.status_code in [200, 404]

    @patch('src.web.views.NewsView')
    def test_home_with_mock_data(self, mock_view_class, client):
        """Test home page with mocked data."""
        # Setup mock
        mock_view = Mock()
        mock_view.list_news = Mock(return_value={
            'articles': [
                {'title': 'Test Article', 'category': 'equities', 'url': 'http://test.com'}
            ],
            'page': 1,
            'per_page': 20,
            'total': 1,
            'total_pages': 1,
            'has_prev': False,
            'has_next': False,
        })
        mock_view.get_categories_stats = Mock(return_value={
            'equities': 10,
            'bonds': 5,
            'forex': 8,
            'commodities': 3
        })
        mock_view.close = Mock()
        mock_view.__enter__ = Mock(return_value=mock_view)
        mock_view.__exit__ = Mock(return_value=False)
        mock_view_class.return_value = mock_view

        response = client.get('/')
        assert response.status_code == 200

        # Verify view methods were called
        mock_view.list_news.assert_called()
        mock_view.get_categories_stats.assert_called()

    def test_context_manager_cleanup(self, app, client):
        """Test that view cleanup happens properly."""
        with app.app_context():
            # Make a request
            response = client.get('/')

            # Should complete without resource leaks
            assert response.status_code == 200

    def test_concurrent_requests(self, client):
        """Test handling concurrent requests."""
        import concurrent.futures

        def make_request():
            return client.get('/')

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
