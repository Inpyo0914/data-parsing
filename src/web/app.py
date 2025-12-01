"""
Flask application factory.

This module creates and configures the Flask application using
the factory pattern for better testing and deployment flexibility.
"""

from flask import Flask, render_template
from typing import Optional, Any

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_app(config: Optional[Any] = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config: Configuration object (uses default if None)

    Returns:
        Configured Flask application

    Example:
        >>> app = create_app()
        >>> app.run(debug=True)
    """
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()

    # Configure Flask from config object
    app.config["SECRET_KEY"] = config.get("flask.secret_key", "dev-secret-key-change-in-production")
    app.config["DEBUG"] = config.get("flask.debug", False)
    app.config["JSON_SORT_KEYS"] = False

    # Template settings
    app.config["TEMPLATES_AUTO_RELOAD"] = app.config["DEBUG"]

    # Store config for use in views
    app.config["APP_CONFIG"] = config

    logger.info(f"Flask app created (debug={app.config['DEBUG']})")

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    register_blueprints(app)

    # Log startup
    logger.info("Flask application initialized successfully")

    return app


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for common HTTP errors.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.warning(f"404 error: {error}")
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(f"500 error: {error}")
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions."""
        logger.exception(f"Unhandled exception: {error}")
        return render_template("errors/500.html"), 500


def register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints.

    Args:
        app: Flask application instance
    """
    from .routes import main_bp, api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    logger.info("Blueprints registered")


# Entry point for running the app
if __name__ == "__main__":
    app = create_app()
    config = app.config["APP_CONFIG"]

    # Get Flask config
    host = config.get("flask.host", "0.0.0.0")
    port = config.get("flask.port", 5000)
    debug = config.get("flask.debug", False)

    logger.info(f"Starting Flask app on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
