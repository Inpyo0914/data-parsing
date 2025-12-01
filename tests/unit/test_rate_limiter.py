"""Unit tests for rate limiter module."""

import pytest
import asyncio
import time
from src.collector.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter class."""

    def test_init_default_values(self):
        """Test RateLimiter initialization with default values."""
        limiter = RateLimiter()
        assert limiter.delay == 1.0
        assert limiter.burst == 1
        assert limiter._tokens == 1

    def test_init_custom_values(self):
        """Test RateLimiter initialization with custom values."""
        limiter = RateLimiter(delay=2.0, burst=5)
        assert limiter.delay == 2.0
        assert limiter.burst == 5
        assert limiter._tokens == 5

    @pytest.mark.asyncio
    async def test_single_acquire(self):
        """Test single token acquisition."""
        limiter = RateLimiter(delay=0.1, burst=1)

        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start

        # Should be nearly instant (< 0.05s)
        assert elapsed < 0.05

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting enforces delay."""
        limiter = RateLimiter(delay=0.2, burst=1)

        # First acquire should be instant
        start = time.monotonic()
        await limiter.acquire()
        first_elapsed = time.monotonic() - start
        assert first_elapsed < 0.05

        # Second acquire should wait ~0.2 seconds
        start = time.monotonic()
        await limiter.acquire()
        second_elapsed = time.monotonic() - start
        assert 0.15 < second_elapsed < 0.3

    @pytest.mark.asyncio
    async def test_burst_tokens(self):
        """Test burst token allowance."""
        limiter = RateLimiter(delay=0.2, burst=3)

        # First 3 acquires should be nearly instant
        start = time.monotonic()
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()
        elapsed = time.monotonic() - start

        # All 3 should complete in < 0.1s
        assert elapsed < 0.1

        # Fourth acquire should wait
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed > 0.15

    @pytest.mark.asyncio
    async def test_token_regeneration(self):
        """Test that tokens regenerate over time."""
        limiter = RateLimiter(delay=0.1, burst=2)

        # Use all tokens
        await limiter.acquire()
        await limiter.acquire()

        # Wait for tokens to regenerate
        await asyncio.sleep(0.3)

        # Should have regenerated ~3 tokens, but burst caps at 2
        # So next 2 acquires should be fast
        start = time.monotonic()
        await limiter.acquire()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_concurrent_acquire(self):
        """Test concurrent acquire calls."""
        limiter = RateLimiter(delay=0.1, burst=1)

        async def acquire_task():
            await limiter.acquire()
            return time.monotonic()

        # Launch 3 concurrent tasks
        start = time.monotonic()
        results = await asyncio.gather(*[acquire_task() for _ in range(3)])

        # They should be spaced ~0.1s apart
        total_time = max(results) - start
        assert 0.15 < total_time < 0.35

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using RateLimiter as async context manager."""
        limiter = RateLimiter(delay=0.1, burst=1)

        start = time.monotonic()
        async with limiter:
            pass
        elapsed = time.monotonic() - start

        # First use should be instant
        assert elapsed < 0.05

        # Second use should wait
        start = time.monotonic()
        async with limiter:
            pass
        elapsed = time.monotonic() - start
        assert elapsed > 0.05

    def test_token_cap(self):
        """Test that tokens don't exceed burst limit."""
        limiter = RateLimiter(delay=0.1, burst=3)

        # Even after waiting, tokens should cap at burst
        assert limiter._tokens == 3

        # Manually set time to simulate long wait
        limiter._last_update = time.monotonic() - 10.0

        # Update tokens (this happens in acquire)
        now = time.monotonic()
        elapsed = now - limiter._last_update
        tokens = min(limiter.burst, limiter._tokens + elapsed / limiter.delay)

        # Should cap at burst (3), not grow to 100
        assert tokens == limiter.burst


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
