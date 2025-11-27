"""
Configuration management for the Financial Data Parser application.

This module handles loading configuration from:
1. YAML config file (config/config.yaml)
2. Environment variables (.env file)
3. Default values

Environment variables take precedence over YAML config.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """
    Configuration manager that loads settings from YAML and environment variables.

    Priority order (highest to lowest):
    1. Environment variables
    2. YAML config file
    3. Default values

    Example:
        >>> config = Config()
        >>> config.load()
        >>> print(config.get('elasticsearch.host'))
        'localhost'
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to YAML config file. If None, uses default location.
        """
        self.config_file = config_file or "config/config.yaml"
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(self, env_file: Optional[str] = ".env") -> None:
        """
        Load configuration from YAML file and environment variables.

        Args:
            env_file: Path to .env file. If None, skips loading .env
        """
        # Load environment variables from .env file
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)

        # Load YAML config
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

        # Override with environment variables
        self._override_from_env()
        self._loaded = True

    def _override_from_env(self) -> None:
        """Override config values with environment variables."""
        # Crawler settings
        if os.getenv("FINANCIAL_JUICE_BASE_URL"):
            self._set_nested("crawler.base_url", os.getenv("FINANCIAL_JUICE_BASE_URL"))
        if os.getenv("CRAWLER_USER_AGENT"):
            self._set_nested("crawler.user_agent", os.getenv("CRAWLER_USER_AGENT"))
        if os.getenv("CRAWLER_DELAY"):
            self._set_nested("crawler.delay", int(os.getenv("CRAWLER_DELAY")))
        if os.getenv("CRAWLER_TIMEOUT"):
            self._set_nested("crawler.timeout", int(os.getenv("CRAWLER_TIMEOUT")))
        if os.getenv("CRAWLER_MAX_RETRIES"):
            self._set_nested("crawler.max_retries", int(os.getenv("CRAWLER_MAX_RETRIES")))

        # Elasticsearch settings
        if os.getenv("ES_HOST"):
            self._set_nested("elasticsearch.host", os.getenv("ES_HOST"))
        if os.getenv("ES_PORT"):
            self._set_nested("elasticsearch.port", int(os.getenv("ES_PORT")))
        if os.getenv("ES_INDEX_PREFIX"):
            self._set_nested("elasticsearch.index_prefix", os.getenv("ES_INDEX_PREFIX"))

        # Flask settings
        if os.getenv("FLASK_HOST"):
            self._set_nested("flask.host", os.getenv("FLASK_HOST"))
        if os.getenv("FLASK_PORT"):
            self._set_nested("flask.port", int(os.getenv("FLASK_PORT")))
        if os.getenv("FLASK_DEBUG"):
            self._set_nested("flask.debug", os.getenv("FLASK_DEBUG").lower() == "true")
        if os.getenv("FLASK_SECRET_KEY"):
            self._set_nested("flask.secret_key", os.getenv("FLASK_SECRET_KEY"))

        # Scheduler settings
        if os.getenv("COLLECTION_SCHEDULE"):
            self._set_nested("scheduler.cron_schedule", os.getenv("COLLECTION_SCHEDULE"))

        # Logging settings
        if os.getenv("LOG_LEVEL"):
            self._set_nested("logging.level", os.getenv("LOG_LEVEL"))
        if os.getenv("LOG_FILE"):
            self._set_nested("logging.file.path", os.getenv("LOG_FILE"))

        # Environment
        if os.getenv("ENVIRONMENT"):
            self._set_nested("app.environment", os.getenv("ENVIRONMENT"))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'elasticsearch.host')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config.get('elasticsearch.host', 'localhost')
            'localhost'
        """
        if not self._loaded:
            self.load()

        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def _set_nested(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration as a dictionary.

        Returns:
            Complete configuration dictionary
        """
        if not self._loaded:
            self.load()
        return self._config.copy()

    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-style access.

        Example:
            >>> config['elasticsearch.host']
            'localhost'
        """
        return self.get(key)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Config loaded={self._loaded}>"


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance

    Example:
        >>> config = get_config()
        >>> es_host = config.get('elasticsearch.host')
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
        _config_instance.load()
    return _config_instance


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration and return as dictionary.

    Args:
        config_file: Path to YAML config file

    Returns:
        Configuration dictionary

    Example:
        >>> config = load_config()
        >>> print(config['elasticsearch']['host'])
        'localhost'
    """
    config = Config(config_file)
    config.load()
    return config.get_all()


# Example usage
if __name__ == "__main__":
    # Test configuration
    config = get_config()

    print("Configuration loaded successfully!")
    print(f"Environment: {config.get('app.environment')}")
    print(f"ES Host: {config.get('elasticsearch.host')}")
    print(f"ES Port: {config.get('elasticsearch.port')}")
    print(f"Crawler URL: {config.get('crawler.base_url')}")
    print(f"Flask Port: {config.get('flask.port')}")
    print(f"Log Level: {config.get('logging.level')}")
