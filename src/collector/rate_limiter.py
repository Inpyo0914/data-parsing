"""
Rate limiter for controlling request frequency to avoid overloading servers.
"""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """
    Rate limiter to control the frequency of requests.

    Uses a token bucket algorithm to allow bursts while maintaining
    an average rate limit.

    Example:
        >>> limiter = RateLimiter(delay=2.0)
        >>> async with limiter:
        ...     # Make request here
        ...     response = await fetch_page(url)
    """

    def __init__(
        self,
        delay: float = 1.0,
        burst: int = 1,
    ):
        """
        Initialize rate limiter.

        Args:
            delay: Minimum delay between requests in seconds
            burst: Maximum number of requests that can be made in a burst
        """
        self.delay = delay
        self.burst = burst
        self._tokens = burst
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        This method will block until a token is available.
        """
        async with self._lock:
            # Refill tokens based on time elapsed
            now = time.monotonic()
            elapsed = now - self._last_update
            self._tokens = min(
                self.burst,
                self._tokens + elapsed / self.delay
            )
            self._last_update = now

            # Wait if no tokens available
            if self._tokens < 1:
                wait_time = (1 - self._tokens) * self.delay
                await asyncio.sleep(wait_time)
                self._tokens = 0
                self._last_update = time.monotonic()
            else:
                self._tokens -= 1

    async def __aenter__(self):
        """Context manager entry - acquire token."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return False

    def set_delay(self, delay: float) -> None:
        """
        Update the delay between requests.

        Args:
            delay: New delay in seconds
        """
        self.delay = delay

    def reset(self) -> None:
        """Reset the rate limiter to initial state."""
        self._tokens = self.burst
        self._last_update = time.monotonic()


# Example usage
if __name__ == "__main__":
    import aiohttp

    async def test_rate_limiter():
        """Test rate limiter with multiple requests."""
        limiter = RateLimiter(delay=2.0, burst=3)

        async def fetch_with_limit(url: str, session: aiohttp.ClientSession):
            """Fetch URL with rate limiting."""
            async with limiter:
                print(f"[{time.strftime('%H:%M:%S')}] Fetching {url}")
                async with session.get(url) as response:
                    return response.status

        urls = [
            "https://httpbin.org/delay/0",
            "https://httpbin.org/delay/0",
            "https://httpbin.org/delay/0",
            "https://httpbin.org/delay/0",
            "https://httpbin.org/delay/0",
        ]

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_with_limit(url, session) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print(f"Results: {results}")

    # Run test
    asyncio.run(test_rate_limiter())
