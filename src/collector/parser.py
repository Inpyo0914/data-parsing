"""
HTML parser for extracting news data from FinancialJuice website.

This module provides functionality to parse HTML and extract structured data.
The selectors are defined as class attributes for easy customization.
"""

from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin

from .exceptions import ParseException
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FinancialJuiceParser:
    """
    Parser for FinancialJuice website HTML.

    This parser uses CSS selectors to extract news data. The selectors
    can be customized by modifying the class attributes.

    Note: The selectors below are placeholders and need to be updated
    based on the actual website structure.
    """

    # CSS Selectors - UPDATE THESE BASED ON ACTUAL SITE STRUCTURE
    ARTICLE_LIST_SELECTOR = "article, .article, .news-item, .post"
    TITLE_SELECTOR = "h2, h3, .title, .headline, .article-title"
    SUMMARY_SELECTOR = ".summary, .excerpt, .description, p"
    LINK_SELECTOR = "a[href]"
    DATE_SELECTOR = "time, .date, .published, .post-date"
    AUTHOR_SELECTOR = ".author, .by-line, .writer"
    CONTENT_SELECTOR = ".content, .article-body, .post-content, article"
    TAG_SELECTOR = ".tag, .label, .category"

    def __init__(self, base_url: str = "https://www.financialjuice.com"):
        """
        Initialize parser.

        Args:
            base_url: Base URL for resolving relative links
        """
        self.base_url = base_url

    def parse_article_list(
        self,
        html: str,
        category: str,
    ) -> List[Dict]:
        """
        Parse a list of articles from HTML.

        Args:
            html: HTML content
            category: Category name (equities, bonds, forex, commodities)

        Returns:
            List of article dictionaries

        Raises:
            ParseException: If parsing fails
        """
        try:
            soup = BeautifulSoup(html, "lxml")
            articles = []

            article_elements = soup.select(self.ARTICLE_LIST_SELECTOR)

            if not article_elements:
                logger.warning(
                    f"No articles found with selector: {self.ARTICLE_LIST_SELECTOR}"
                )
                return []

            for element in article_elements:
                try:
                    article_data = self._extract_article_summary(element, category)
                    if article_data and article_data.get("title"):
                        articles.append(article_data)
                except Exception as e:
                    logger.warning(f"Failed to parse article element: {e}")
                    continue

            logger.info(f"Parsed {len(articles)} articles from {category}")
            return articles

        except Exception as e:
            raise ParseException(f"Failed to parse article list: {e}")

    def parse_article_detail(self, html: str) -> Dict:
        """
        Parse detailed article information.

        Args:
            html: HTML content of article detail page

        Returns:
            Article dictionary with full content

        Raises:
            ParseException: If parsing fails
        """
        try:
            soup = BeautifulSoup(html, "lxml")

            return {
                "title": self._extract_title(soup),
                "content": self._extract_content(soup),
                "author": self._extract_author(soup),
                "published_date": self._extract_date(soup),
                "tags": self._extract_tags(soup),
            }

        except Exception as e:
            raise ParseException(f"Failed to parse article detail: {e}")

    def _extract_article_summary(self, element, category: str) -> Dict:
        """Extract summary information from an article element."""
        title = self._extract_title(element)
        url = self._extract_url(element)

        # Resolve relative URLs
        if url and not url.startswith("http"):
            url = urljoin(self.base_url, url)

        return {
            "title": title,
            "summary": self._extract_summary(element),
            "url": url,
            "published_date": self._extract_date(element),
            "category": category,
            "crawled_at": datetime.utcnow().isoformat(),
        }

    def _extract_title(self, element) -> str:
        """Extract title from element."""
        title_elem = element.select_one(self.TITLE_SELECTOR)
        if title_elem:
            return self._clean_text(title_elem.get_text())
        return ""

    def _extract_summary(self, element) -> str:
        """Extract summary/excerpt from element."""
        summary_elem = element.select_one(self.SUMMARY_SELECTOR)
        if summary_elem:
            return self._clean_text(summary_elem.get_text())
        return ""

    def _extract_content(self, element) -> str:
        """Extract full content from element."""
        content_elem = element.select_one(self.CONTENT_SELECTOR)
        if not content_elem:
            return ""

        # Remove unwanted elements
        for unwanted in content_elem.select("script, style, iframe, ads"):
            unwanted.decompose()

        return self._clean_text(content_elem.get_text(separator="\n"))

    def _extract_url(self, element) -> str:
        """Extract URL from element."""
        link_elem = element.select_one(self.LINK_SELECTOR)
        if link_elem and link_elem.has_attr("href"):
            return link_elem["href"]
        return ""

    def _extract_date(self, element) -> Optional[str]:
        """Extract and parse date from element."""
        date_elem = element.select_one(self.DATE_SELECTOR)
        if not date_elem:
            return None

        # Try datetime attribute first
        if date_elem.has_attr("datetime"):
            date_str = date_elem["datetime"]
        else:
            date_str = date_elem.get_text(strip=True)

        return self._parse_date_string(date_str)

    def _extract_author(self, element) -> str:
        """Extract author name from element."""
        author_elem = element.select_one(self.AUTHOR_SELECTOR)
        if author_elem:
            return self._clean_text(author_elem.get_text())
        return ""

    def _extract_tags(self, element) -> List[str]:
        """Extract tags/categories from element."""
        tag_elems = element.select(self.TAG_SELECTOR)
        return [self._clean_text(tag.get_text()) for tag in tag_elems]

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def _parse_date_string(date_str: str) -> Optional[str]:
        """
        Parse date string to ISO format.

        This method attempts to parse various date formats.
        Add more formats as needed based on the actual site.

        Args:
            date_str: Date string to parse

        Returns:
            ISO format date string or None if parsing fails
        """
        if not date_str:
            return None

        # Common date formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",  # ISO format
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%b %d, %Y",  # Dec 27, 2025
            "%B %d, %Y",  # December 27, 2025
            "%d %b %Y",  # 27 Dec 2025
            "%d %B %Y",  # 27 December 2025
            "%m/%d/%Y",  # 12/27/2025
            "%d/%m/%Y",  # 27/12/2025
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.isoformat()
            except ValueError:
                continue

        logger.warning(f"Failed to parse date: {date_str}")
        return None

    def update_selectors(
        self,
        article_list: Optional[str] = None,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        link: Optional[str] = None,
        date: Optional[str] = None,
        content: Optional[str] = None,
    ) -> None:
        """
        Update CSS selectors for parsing.

        Use this method to customize selectors based on actual site structure.

        Args:
            article_list: Selector for article list items
            title: Selector for article title
            summary: Selector for article summary
            link: Selector for article link
            date: Selector for publish date
            content: Selector for article content
        """
        if article_list:
            self.ARTICLE_LIST_SELECTOR = article_list
        if title:
            self.TITLE_SELECTOR = title
        if summary:
            self.SUMMARY_SELECTOR = summary
        if link:
            self.LINK_SELECTOR = link
        if date:
            self.DATE_SELECTOR = date
        if content:
            self.CONTENT_SELECTOR = content

        logger.info("Updated parser selectors")


# Example usage
if __name__ == "__main__":
    # Test with sample HTML
    sample_html = """
    <html>
        <body>
            <article>
                <h2>Stock Market Hits Record High</h2>
                <p class="summary">Markets soared today...</p>
                <a href="/articles/stock-market-high">Read more</a>
                <time datetime="2025-11-27T10:00:00">Nov 27, 2025</time>
            </article>
        </body>
    </html>
    """

    parser = FinancialJuiceParser()
    articles = parser.parse_article_list(sample_html, "equities")
    print(f"Parsed {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title']}")
