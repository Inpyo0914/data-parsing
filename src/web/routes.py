"""
Flask routes and blueprints.

This module defines all URL routes for the web application,
including both HTML pages and JSON API endpoints.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from typing import Dict, Any

from .views import NewsView
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprints
main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__)


def get_news_view() -> NewsView:
    """
    Get NewsView instance with app config.

    Returns:
        NewsView instance
    """
    config = current_app.config.get("APP_CONFIG")
    return NewsView(config=config)


# ============================================================================
# Main HTML Routes
# ============================================================================

@main_bp.route("/")
def index():
    """
    Homepage showing latest news from all categories.
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Validate and limit per_page
        per_page = max(1, min(per_page, 100))

        with get_news_view() as view:
            data = view.list_news(page=page, per_page=per_page)
            stats = view.get_categories_stats()

        return render_template(
            "index.html",
            **data,
            stats=stats,
            title="Financial News - Latest Updates"
        )

    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template(
            "errors/500.html",
            error="Failed to load news"
        ), 500


@main_bp.route("/category/<category>")
def category(category: str):
    """
    Show news for a specific category.

    Args:
        category: Category name (equities, bonds, forex, commodities)
    """
    try:
        # Validate category
        valid_categories = ["equities", "bonds", "forex", "commodities"]
        if category not in valid_categories:
            return render_template(
                "errors/404.html",
                error=f"Category '{category}' not found"
            ), 404

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Validate and limit per_page
        per_page = max(1, min(per_page, 100))

        with get_news_view() as view:
            data = view.list_news(page=page, per_page=per_page, category=category)
            stats = view.get_categories_stats()

        return render_template(
            "category.html",
            **data,
            stats=stats,
            title=f"{category.capitalize()} News"
        )

    except Exception as e:
        logger.error(f"Error in category route: {e}")
        return render_template(
            "errors/500.html",
            error="Failed to load category"
        ), 500


@main_bp.route("/search")
def search():
    """
    Search page with filters.
    """
    try:
        query = request.args.get("q", "")
        category = request.args.get("category", None)
        date_from = request.args.get("date_from", None)
        date_to = request.args.get("date_to", None)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Validate and limit per_page
        per_page = max(1, min(per_page, 100))

        with get_news_view() as view:
            data = view.search_news(
                query_string=query,
                page=page,
                per_page=per_page,
                category=category,
                date_from=date_from,
                date_to=date_to
            )
            stats = view.get_categories_stats()

        return render_template(
            "search.html",
            **data,
            stats=stats,
            title="Search Results"
        )

    except Exception as e:
        logger.error(f"Error in search route: {e}")
        return render_template(
            "errors/500.html",
            error="Search failed"
        ), 500


@main_bp.route("/news/<path:news_id>")
def news_detail(news_id: str):
    """
    Show detailed view of a single news article.

    Args:
        news_id: News ID (typically the URL)
    """
    try:
        with get_news_view() as view:
            article = view.get_news_detail(news_id)
            stats = view.get_categories_stats()

        if article is None:
            return render_template(
                "errors/404.html",
                error="Article not found"
            ), 404

        return render_template(
            "detail.html",
            article=article,
            stats=stats,
            title=article.get("title", "News Article")
        )

    except Exception as e:
        logger.error(f"Error in news_detail route: {e}")
        return render_template(
            "errors/500.html",
            error="Failed to load article"
        ), 500


# ============================================================================
# JSON API Routes
# ============================================================================

@api_bp.route("/news")
def api_list_news():
    """
    JSON API endpoint for listing news.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - category: Category filter (optional)
        - sort_by: Sort field (default: crawled_at)

    Returns:
        JSON response with news list
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        category = request.args.get("category", None)
        sort_by = request.args.get("sort_by", "crawled_at")

        # Validate and limit per_page
        per_page = max(1, min(per_page, 100))

        with get_news_view() as view:
            data = view.list_news(
                page=page,
                per_page=per_page,
                category=category,
                sort_by=sort_by
            )

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        logger.error(f"Error in api_list_news: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/search")
def api_search():
    """
    JSON API endpoint for searching news.

    Query parameters:
        - q: Search query
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - category: Category filter (optional)
        - date_from: Start date (ISO format, optional)
        - date_to: End date (ISO format, optional)

    Returns:
        JSON response with search results
    """
    try:
        query = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        category = request.args.get("category", None)
        date_from = request.args.get("date_from", None)
        date_to = request.args.get("date_to", None)

        # Validate and limit per_page
        per_page = max(1, min(per_page, 100))

        with get_news_view() as view:
            data = view.search_news(
                query_string=query,
                page=page,
                per_page=per_page,
                category=category,
                date_from=date_from,
                date_to=date_to
            )

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        logger.error(f"Error in api_search: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/news/<path:news_id>")
def api_news_detail(news_id: str):
    """
    JSON API endpoint for getting news detail.

    Args:
        news_id: News ID

    Returns:
        JSON response with article details
    """
    try:
        with get_news_view() as view:
            article = view.get_news_detail(news_id)

        if article is None:
            return jsonify({
                "success": False,
                "error": "Article not found"
            }), 404

        return jsonify({
            "success": True,
            "data": article
        })

    except Exception as e:
        logger.error(f"Error in api_news_detail: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/stats")
def api_stats():
    """
    JSON API endpoint for getting category statistics.

    Returns:
        JSON response with article counts by category
    """
    try:
        with get_news_view() as view:
            stats = view.get_categories_stats()

        return jsonify({
            "success": True,
            "data": stats
        })

    except Exception as e:
        logger.error(f"Error in api_stats: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
