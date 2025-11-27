"""
Custom exceptions for the crawler module.
"""


class CrawlerException(Exception):
    """Base exception for all crawler-related errors."""
    pass


class FetchException(CrawlerException):
    """Exception raised when fetching a page fails."""
    pass


class ParseException(CrawlerException):
    """Exception raised when parsing HTML fails."""
    pass


class RateLimitException(CrawlerException):
    """Exception raised when rate limit is exceeded."""
    pass


class ValidationException(CrawlerException):
    """Exception raised when data validation fails."""
    pass
