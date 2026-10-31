"""CIVORA Developer Platform Sliding-Window Rate Limiter.

Enforces per-key requests-per-minute (RPM) limits with standard rate limit headers
and 429 Too Many Requests rejection.
"""

from __future__ import annotations

import collections
import threading
import time
from typing import Dict, Tuple

from fastapi import HTTPException


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter tracking request timestamps per API key."""

    def __init__(self, window_seconds: float = 60.0):
        self.window_seconds = window_seconds
        self._history: Dict[str, collections.deque] = collections.defaultdict(collections.deque)
        self._lock = threading.Lock()

    def check_and_record(self, key_id: str, limit_rpm: int) -> Tuple[bool, int, float]:
        """Check if request is within limit and record timestamp.
        
        Returns:
            (allowed: bool, remaining_requests: int, reset_seconds: float)
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            queue = self._history[key_id]

            # Remove timestamps outside the sliding window
            while queue and queue[0] < window_start:
                queue.popleft()

            current_count = len(queue)
            if current_count >= limit_rpm:
                # Calculate time until the oldest request in the window expires
                oldest = queue[0]
                reset_seconds = max(0.1, round((oldest + self.window_seconds) - now, 2))
                return False, 0, reset_seconds

            # Record this request
            queue.append(now)
            remaining = max(0, limit_rpm - (current_count + 1))
            return True, remaining, self.window_seconds

    def enforce(self, key_id: str, limit_rpm: int) -> Dict[str, str]:
        """Enforce rate limit, raising HTTP 429 if exceeded, or returning ratelimit headers."""
        allowed, remaining, reset_secs = self.check_and_record(key_id, limit_rpm)
        headers = {
            "x-ratelimit-limit-requests": str(limit_rpm),
            "x-ratelimit-remaining-requests": str(remaining),
            "x-ratelimit-reset-requests": f"{reset_secs:.1f}s",
        }
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": {
                        "message": f"Rate limit reached for requests: {limit_rpm} requests per minute. Please back off and retry in {reset_secs:.1f} seconds.",
                        "type": "rate_limit_error",
                        "param": None,
                        "code": "rate_limit_exceeded",
                    }
                },
                headers=headers,
            )
        return headers


# Global singleton instance
rate_limiter = SlidingWindowRateLimiter(window_seconds=60.0)

